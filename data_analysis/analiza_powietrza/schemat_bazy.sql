-- Tabela 1: Historia pomiarow zanieczyszczen
CREATE TABLE pomiary_smogu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    miasto TEXT NOT NULL,
    pm10 REAL,
    pm25 REAL,
    klasyfikacja TEXT,
    data_pobrania DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela 2: Mapowanie mniejszych miast i kodow pocztowych
CREATE TABLE slownik_miast (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    miasto_uzytkownika TEXT NOT NULL,
    kod_pocztowy TEXT NOT NULL,
    najblizsza_stacja TEXT NOT NULL
);