class FilmeLocadora():
    def __init__(self, id, titulo, diretor, ano, genero, sinopse="", alugado=False):
        self.id = id
        self.titulo = titulo
        self.diretor = diretor
        self.ano = ano
        self.genero = genero
        self.sinopse = sinopse
        self.alugado = alugado
