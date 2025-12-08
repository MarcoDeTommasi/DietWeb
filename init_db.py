from database import engine
from models import Base
from database import engine, SessionLocal
from models import Base, User
import json

def init_db():
    """
    Crea tutte le tabelle definite nei modelli.
    """
    print("Creazione delle tabelle nel database...")
    Base.metadata.create_all(bind=engine)
    print("Tabelle create con successo!")
    # Aggiungi un'utenza di default
    add_default_user()

def add_default_user():
    """
    Aggiunge un'utenza di default con un dict_lunch precompilato.
    """
    db = SessionLocal()
    try:
        # Controlla se l'utenza di default esiste già
        default_username = "MarcoDefault"
        user = db.query(User).filter(User.username == default_username).first()
        if not user:
            # Dizionario lunch precompilato


            # Crea l'utente di default
            default_user = User(
                username=default_username,
                password="DietAppV0",  # Assicurati di hashare la password in un'app reale
                email="marco.detommasi@example.com",
                first_name="Marco",
                last_name="De Tommasi",
                dieta=json.dumps(
                    {'Lunedì': {'Colazione': {'latte_parzialmente_scremato': {'Quantità': 200, 'Unità': 'ml'
                        }, 'fette_biscottate': {'Quantità': 40, 'Unità': 'g'
                        }, 'marmellata': {'Quantità': 40, 'Unità': 'g'
                        }
                    }, 'Pranzo': {'fagioli': {'Quantità': 80, 'Unità': 'g'
                        }, 'pane_integrale': {'Quantità': 60, 'Unità': 'g'
                        }, 'verdura': {'Quantità': 200, 'Unità': 'g'
                        }, 'frutto': {'Quantità': 1, 'Unità': 'pz'
                        }
                    }, 'Cena': {'merluzzo': {'Quantità': 200, 'Unità': 'g'
                        }, 'verdura': {'Quantità': 200, 'Unità': 'g'
                        }, 'ortaggi': {'Quantità': 100, 'Unità': 'g'
                        }, 'piadina': {'Quantità': 55, 'Unità': 'g'
                        }
                    }, 'Spuntino Mattina': {'frutto': {'Quantità': 1, 'Unità': 'pz'
                        }, 'mandorle': {'Quantità': 3, 'Unità': 'pz'
                        }
                    }, 'Spuntino Pomeriggio': {'pane_integrale': {'Quantità': 50, 'Unità': 'g'
                        }, 'fesa_di_tacchino': {'Quantità': 50, 'Unità': 'g'
                        }
                    }
                }, 'Martedì': {'Colazione': {'yogurt_greco': {'Quantità': 170, 'Unità': 'g'
                        }, 'cereali_integrali': {'Quantità': 50, 'Unità': 'g'
                        }, 'frutto': {'Quantità': 1, 'Unità': 'pz'
                        }
                    }, 'Pranzo': {'farro': {'Quantità': 70, 'Unità': 'g'
                        }, 'uova': {'Quantità': 2, 'Unità': 'pz'
                        }, 'verdura': {'Quantità': 200, 'Unità': 'g'
                        }, 'frutto': {'Quantità': 1, 'Unità': 'pz'
                        }
                    }, 'Cena': {'petto_di_pollo': {'Quantità': 200, 'Unità': 'g'
                        }, 'verdura': {'Quantità': 200, 'Unità': 'g'
                        }, 'ortaggi': {'Quantità': 100, 'Unità': 'g'
                        }, 'piadina': {'Quantità': 55, 'Unità': 'g'
                        }
                    }, 'Spuntino Mattina': {'frutto': {'Quantità': 1, 'Unità': 'pz'
                        }, 'mandorle': {'Quantità': 4, 'Unità': 'pz'
                        }
                    }, 'Spuntino Pomeriggio': {'pane_integrale': {'Quantità': 50, 'Unità': 'g'
                        }, 'pomodori': {'Quantità': 50, 'Unità': 'g'
                        }
                    }
                }, 'Mercoledì': {'Colazione': {'succo_di_frutta': {'Quantità': 200, 'Unità': 'ml'
                        }, 'pane_integrale': {'Quantità': 50, 'Unità': 'g'
                        }, 'prosciutto_crudo': {'Quantità': 40, 'Unità': 'g'
                        }
                    }, 'Pranzo': {'tonno': {'Quantità': 120, 'Unità': 'g'
                        }, 'verdura': {'Quantità': 200, 'Unità': 'g'
                        }, 'cous_cous': {'Quantità': 70, 'Unità': 'g'
                        }, 'frutto': {'Quantità': 1, 'Unità': 'pz'
                        }
                    }, 'Cena': {'ricotta_di_mucca': {'Quantità': 120, 'Unità': 'g'
                        }, 'verdura': {'Quantità': 200, 'Unità': 'g'
                        }, 'ortaggi': {'Quantità': 100, 'Unità': 'g'
                        }, 'piadina': {'Quantità': 55, 'Unità': 'g'
                        }
                    }, 'Spuntino Mattina': {'frutto': {'Quantità': 1, 'Unità': 'pz'
                        }
                    }, 'Spuntino Pomeriggio': {'pane_integrale': {'Quantità': 50, 'Unità': 'g'
                        }, 'pomodori': {'Quantità': 50, 'Unità': 'g'
                        }
                    }
                }, 'Giovedì': {'Colazione': {'yogurt_greco': {'Quantità': 170, 'Unità': 'g'
                        }, 'biscotti_secchi': {'Quantità': 7, 'Unità': 'pz'
                        }, 'marmellata': {'Quantità': 50, 'Unità': 'g'
                        }
                    }, 'Pranzo': {'patate': {'Quantità': 300, 'Unità': 'g'
                        }, 'merluzzo': {'Quantità': 200, 'Unità': 'g'
                        }, 'verdura': {'Quantità': 200, 'Unità': 'g'
                        }
                    }, 'Cena': {'fesa_di_tacchino': {'Quantità': 120, 'Unità': 'g'
                        }, 'verdura': {'Quantità': 200, 'Unità': 'g'
                        }, 'ortaggi': {'Quantità': 100, 'Unità': 'g'
                        }, 'piadina': {'Quantità': 55, 'Unità': 'g'
                        }
                    }, 'Spuntino Mattina': {'frutto': {'Quantità': 1, 'Unità': 'pz'
                        }, 'mandorle': {'Quantità': 4, 'Unità': 'pz'
                        }
                    }, 'Spuntino Pomeriggio': {'pane_integrale': {'Quantità': 50, 'Unità': 'g'
                        }, 'pomodori': {'Quantità': 50, 'Unità': 'g'
                        }
                    }
                }, 'Venerdì': {'Colazione': {'latte_parzialmente_scremato': {'Quantità': 200, 'Unità': 'g'
                        }, 'marmellata': {'Quantità': 40, 'Unità': 'g'
                        }, 'fette_biscottate': {'Quantità': 40, 'Unità': 'g'
                        }
                    }, 'Pranzo': {'pasta_integrale': {'Quantità': 60, 'Unità': 'g'
                        }, 'fagioli': {'Quantità': 50, 'Unità': 'g'
                        }, 'fesa_di_tacchino': {'Quantità': 50, 'Unità': 'g'
                        }, 'verdura': {'Quantità': 200, 'Unità': 'g'
                        }, 'frutto': {'Quantità': 1, 'Unità': 'pz'
                        }
                    }, 'Cena': {'uova': {'Quantità': 2, 'Unità': 'pz'
                        }, 'verdura': {'Quantità': 200, 'Unità': 'g'
                        }, 'ortaggi': {'Quantità': 100, 'Unità': 'g'
                        }, 'piadina': {'Quantità': 55, 'Unità': 'g'
                        }
                    }, 'Spuntino Mattina': {'frutto': {'Quantità': 1, 'Unità': 'pz'
                        }, 'mandorle': {'Quantità': 8, 'Unità': 'pz'
                        }
                    }, 'Spuntino Pomeriggio': {'pane_integrale': {'Quantità': 50, 'Unità': 'g'
                        }, 'pomodori': {'Quantità': 50, 'Unità': 'g'
                        }
                    }
                }, 'Sabato': {'Colazione': {'yogurt_greco': {'Quantità': 170, 'Unità': 'g'
                        }, 'cereali_integrali': {'Quantità': 50, 'Unità': 'g'
                        }, 'frutto': {'Quantità': 1, 'Unità': 'pz'
                        }
                    }, 'Pranzo': {'petto_di_pollo': {'Quantità': 220, 'Unità': 'g'
                        }, 'verdura': {'Quantità': 200, 'Unità': 'g'
                        }, 'pane_integrale': {'Quantità': 60, 'Unità': 'g'
                        }
                    }, 'Cena': {'pizza_margherita': {'Quantità': 1, 'Unità': 'pz'
                        }
                    }, 'Spuntino Mattina': {'mandorle': {'Quantità': 8, 'Unità': 'pz'
                        }
                    }, 'Spuntino Pomeriggio': {'yogurt_greco': {'Quantità': 125, 'Unità': 'g'
                        }
                    }
                }, 'Domenica': {'Colazione': {'succo_di_frutta': {'Quantità': 200, 'Unità': 'ml'
                        }, 'pane_integrale': {'Quantità': 50, 'Unità': 'g'
                        }, 'prosciutto_crudo': {'Quantità': 40, 'Unità': 'g'
                        }
                    }, 'Pranzo': {'pasta_integrale': {'Quantità': 80, 'Unità': 'g'
                        }, 'filetto_magro_di_bovino_adulto': {'Quantità': 150, 'Unità': 'g'
                        }, 'verdura': {'Quantità': 200, 'Unità': 'g'
                        }, 'frutto': {'Quantità': 1, 'Unità': 'pz'
                        }
                    }, 'Cena': {'salmone_fresco': {'Quantità': 100, 'Unità': 'g'
                        }, 'verdura': {'Quantità': 200, 'Unità': 'g'
                        }, 'ortaggi': {'Quantità': 100, 'Unità': 'g'
                        }, 'piadina': {'Quantità': 55, 'Unità': 'g'
                        }
                    }, 'Spuntino Mattina': {'yogurt_greco': {'Quantità': 125, 'Unità': 'g'
                        }
                    }, 'Spuntino Pomeriggio': {'crackers_integrali': {'Quantità': 1, 'Unità': 'pz'
                        }
                    }
                }
            }),  # Salva il dict_lunch come JSON
            lista_alimenti=json.dumps(['biscotti_secchi', 'cereali_integrali', 'cous_cous', 'crackers_integrali', 'fagioli', 'farro', 'fesa_di_tacchino', 'fette_biscottate', 'filetto_magro_di_bovino_adulto', 'frutto', 'latte_parzialmente_scremato', 'mandorle', 'marmellata', 'merluzzo', 'ortaggi', 'pane_integrale', 'pasta_integrale', 'patate', 'petto_di_pollo', 'piadina', 'pizza_margherita', 'pomodori', 'prosciutto_crudo', 'ricotta_di_mucca', 'salmone_fresco', 'succo_di_frutta', 'tonno', 'uova', 'verdura', 'yogurt_greco'])
            )
            db.add(default_user)
            db.commit()
            print(f"✅ Utenza di default '{default_username}' creata con successo!")
        else:
            print(f"ℹ️ L'utenza di default '{default_username}' esiste già.")
    except Exception as e:
        print(f"⚠️ Errore durante la creazione dell'utenza di default: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()