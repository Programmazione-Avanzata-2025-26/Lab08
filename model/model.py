from database.impianto_DAO import ImpiantoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        result = []

        for impianto in self._impianti:
            consumi = impianto.get_consumi()
            consumi_mese = [c.kwh for c in consumi if c.data.month == mese]
            media = 0 if consumi_mese is None else sum(consumi_mese) / len(consumi_mese)
            result.append((impianto.nome, media))

        return result

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        # 🟢 Condizione Terminale
        if len(sequenza_parziale) == 7:  # 7 giorni schedulati
            if costo_corrente < self.__costo_ottimo or self.__costo_ottimo == -1:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale[:]
            return

        for imp_id in consumi_settimana.keys():
            # 🔵 Calcola Parziale
            costo = consumi_settimana[imp_id][giorno - 1]
            if ultimo_impianto is not None and imp_id != ultimo_impianto:
                costo += 5
            sequenza_parziale.append(imp_id)

            # 🟡 Nessun filtro necessario quindi chiamo direttamente la ricorsione per il livello successivo
            self.__ricorsione(sequenza_parziale, giorno + 1, imp_id, costo_corrente + costo, consumi_settimana)

            # 🟣 Backtracking
            sequenza_parziale.pop()

    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        consumi_settimana = {}
        for impianto in self._impianti:
            consumi = impianto.get_consumi()

            # Filtra per il mese
            consumi_mese = [c for c in consumi if c.data.month == mese]

            # Ordina per data
            consumi_mese.sort(key=lambda c: c.data)

            # Prendi solo i primi 7 giorni
            consumi_settimana[impianto.id] = [c.kwh for c in consumi_mese[:7]]

        return consumi_settimana

