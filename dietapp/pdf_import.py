from __future__ import annotations

import json
import re
from collections.abc import Iterable
from functools import lru_cache

import fitz
from openai import OpenAI

from dietapp.config import get_settings
from dietapp.domain import normalise_food_name


MAX_PDF_BYTES = 10 * 1024 * 1024
MAX_PDF_PAGES = 40


class PdfImportError(RuntimeError):
    pass


def split_text(text: str, chunk_size: int = 4_000, overlap: int = 250) -> list[str]:
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Dimensione chunk o sovrapposizione non valida.")
    compact = re.sub(r"[ \t]+", " ", text)
    chunks: list[str] = []
    start = 0
    while start < len(compact):
        end = min(start + chunk_size, len(compact))
        chunks.append(compact[start:end])
        if end == len(compact):
            break
        start = end - overlap
    return chunks


def extract_pdf_text(pdf_bytes: bytes) -> str:
    if not pdf_bytes:
        raise PdfImportError("Il PDF è vuoto.")
    if len(pdf_bytes) > MAX_PDF_BYTES:
        raise PdfImportError("Il PDF supera il limite di 10 MB.")
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
            if document.page_count > MAX_PDF_PAGES:
                raise PdfImportError(
                    f"Il PDF supera il limite di {MAX_PDF_PAGES} pagine."
                )
            text = "\n".join(page.get_text("text") for page in document)
    except PdfImportError:
        raise
    except Exception as error:
        raise PdfImportError("Non è stato possibile leggere il PDF.") from error
    if not text.strip():
        raise PdfImportError(
            "Il PDF non contiene testo estraibile. I PDF scansionati richiedono OCR."
        )
    return text


@lru_cache(maxsize=1)
def _client() -> OpenAI:
    settings = get_settings()
    if not settings.openrouter_api_key:
        raise PdfImportError(
            "OPENROUTER_API_KEY non configurata: inserisci gli alimenti manualmente."
        )
    return OpenAI(
        base_url=settings.openrouter_api_url,
        api_key=settings.openrouter_api_key,
        timeout=30,
        max_retries=2,
    )


def _parse_foods(response: str) -> list[str]:
    text = response.strip()
    candidates = [text]
    object_match = re.search(r"\{[\s\S]*\}", text)
    array_match = re.search(r"\[[\s\S]*\]", text)
    if object_match:
        candidates.append(object_match.group(0))
    if array_match:
        candidates.append(array_match.group(0))

    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        values = payload.get("foods", []) if isinstance(payload, dict) else payload
        if isinstance(values, list):
            return [
                normalise_food_name(value)
                for value in values
                if isinstance(value, str) and normalise_food_name(value)
            ]
    raise PdfImportError("Il servizio AI ha restituito una risposta non valida.")


def extract_foods_from_chunks(chunks: Iterable[str]) -> list[str]:
    settings = get_settings()
    foods: set[str] = set()
    for chunk in chunks:
        prompt = (
            "Estrai tutti gli alimenti dal frammento di piano alimentare. "
            "Non includere pasti, giorni, quantità, unità, alternative o aggettivi "
            "non necessari. Rispondi solo con JSON nel formato "
            '{"foods":["alimento_uno","alimento_due"]}. '
            "Usa minuscole, niente accenti e underscore al posto degli spazi.\n\n"
            f"TESTO:\n{chunk}"
        )
        try:
            completion = _client().chat.completions.create(
                model=settings.openrouter_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=700,
            )
            content = completion.choices[0].message.content or ""
            foods.update(_parse_foods(content))
        except PdfImportError:
            raise
        except Exception as error:
            raise PdfImportError(
                "Il servizio di estrazione AI non è al momento disponibile."
            ) from error
    return sorted(foods)


def get_food_list_from_pdf(pdf_bytes: bytes) -> list[str]:
    text = extract_pdf_text(pdf_bytes)
    return extract_foods_from_chunks(split_text(text))
