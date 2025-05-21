# 🌊 Simulação Argo & Altimetria: Relação entre Altura da Superfície do Mar e Termoclina 🐠

Este projeto analisa a relação entre a altura da superfície do mar (AASM) e a profundidade da termoclina usando dados de flutuadores Argo e altimetria.

---

## 🚀 Descrição

O código realiza:

- Leitura de arquivos NetCDF contendo dados Argo e altimetria.
- Filtragem temporal para os anos de 2015 e 2016.
- Análise da temperatura e salinidade em diferentes estações (verão e inverno).
- Cálculo da profundidade da isoterma de 8ºC (termoclina).
- Criação de gráficos: mapa da AASM com rota do Argo, diagrama TS com curvas de densidade, diagrama de Hovmöller e gráficos da variação da termoclina.
- Salvamento dos gráficos em um PDF para análise posterior.

---

## 📂 Estrutura dos Arquivos

- `B5903118_argo.nc` - Dados Argo (perfil de temperatura, salinidade, pressão, coordenadas, tempo).
- `AtlSW_CMEMS.nc` - Dados de altimetria (altura da superfície do mar, latitude, longitude, tempo).
- `simulacao_argo_altimetria.py` - Código principal da análise e geração dos gráficos.
- `figuras_analise_argo_altimetro.pdf` - Resultado gerado pelo script com os gráficos.

---

## ⚙️ Como usar

1. Clone o repositório:

```bash
git clone https://github.com/seuusuario/seuprojeto.git
cd seuprojeto
```

2. Instale as dependências (recomendado criar um ambiente virtual):

```bash
pip install -r requirements.txt
```

3. Execute o script:

```bash
python simulacao_argo_altimetria.py
```

4. Confira o arquivo PDF `figuras_analise_argo_altimetro.pdf` com as figuras geradas.

---

## 🧰 Dependências

- numpy
- netCDF4
- matplotlib
- scipy
- gsw

Todas estão listadas no `requirements.txt`.

---

## 🤝 Contribuições

Contribuições são bem-vindas! Faça um fork, crie uma branch e envie um pull request.

---

## 📄 Licença

MIT License © 2025 Seu Nome

---

## 📬 Contato

Para dúvidas, envie e-mail para: seuemail@exemplo.com

---

**Divirta-se explorando a oceanografia com Python! 🐬🌐**
