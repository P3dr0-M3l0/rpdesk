from abc import ABC, abstractmethod


# =====================================================
# Base Abstrata de Encontro ---------------------------
# =====================================================
class Encontro(ABC):
    """
    Classe base abstrata para qualquer tipo de encontro
    dentro de uma expedição.
    """
    @abstractmethod
    def executar(self, membros_equipe: list, motor_combate, event_manager) -> dict:
        """
        Executa o encontro e retorna um dicionário com o
        resultado da interação.

        Retorno esperado:
            {
                'tipo'            : str,   # 'combate' | 'texto'
                'sucesso'         : bool,  # False encerra a expedição
                'herois_vivos'    : list,  # Instâncias de Heroi que sobreviveram
                'herois_mortos'   : list,  # Instâncias de Heroi que caíram aqui
                'itens_saqueados' : list,
                'itens_recuperados': list,
                'itens_perdidos'  : list,
                'xp_ganho'        : int,
                'ouro_ganho'      : int,
            }
        """
        ...
