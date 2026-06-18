# ⚡ Biogas Simulator

**Micro SaaS — Simulador de Viabilidade Econômica de Biodigestores**

> Descubra em segundos: investimento, payback, ROI e geração de energia para sua propriedade rural. **100% gratuito.**

---

## 🎯 O que é

O **Biogas Simulator** é um Micro SaaS técnico que calcula a viabilidade econômica de projetos de biodigestão para propriedades rurais. Desenvolvido por um engenheiro especialista em agroenergia, com parâmetros técnicos reais do setor.

### Por que isso importa

- **40% das propriedades rurais** no Brasil produzem dejetos com potencial energético desperdiçado
- Decisão de investimento em biodigestor envolve **R$ 50k–500k** — erro é caro
- Consultoria técnica tradicional custa **R$ 5k–15k** por estudo de viabilidade
- Nossa ferramenta entrega **mesma precisão, instantaneamente, de graça**

---

## 🚀 Stack 100% Local

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.13 + Flask |
| Engine | Modelo físico-químico de biodigestão |
| PDF | WeasyPrint (HTML→PDF) |
| Frontend | Vanilla JS + CSS3 |
| IA | Ollama (Qwen 3.5 9B) — geração de relatórios inteligentes |
| Deploy | Local + Cloudflare Tunnel |

**Zero APIs pagas. Zero dependências externas. Privacidade total.**

---

## 📊 Funcionalidades

### ✅ Gratuito (Freemium)
- [x] Simulação completa de viabilidade
- [x] Comparativo entre 4 tipos de biodigestor
- [x] Cálculo de payback, ROI, VPL, TIR
- [x] Projeção de geração de energia (kWh/dia, mês, ano)
- [x] Estimativa de crédito de carbono
- [x] Recomendações técnicas personalizadas
- [x] Relatório PDF básico

### 💎 PRO (R$ 97/mês ou R$ 497 único)
- [ ] Cenários customizados (temperatura, altitude, tipo de substrato)
- [ ] Comparativo detalhado com gráficos interativos
- [ ] Relatório técnico completo (20+ páginas)
- [ ] Análise de sensibilidade (variação de preços)
- [ ] Suporte técnico direto com engenheiro
- [ ] API para integração com sistemas da propriedade

---

## 🏗️ Arquitetura

```
biogas-simulator/
├── src/
│   ├── engine/
│   │   └── simulator.py          # Motor de cálculo técnico
│   └── web/
│       ├── app.py                # Flask API + servidor
│       ├── templates/
│       │   └── index.html        # Interface única
│       └── static/
│           ├── css/style.css     # Design system
│           └── js/app.js         # Frontend app
├── requirements.txt
└── README.md
```

---

## 🧮 Modelo de Cálculo

### Parâmetros Técnicos

| Animal | Dejetos (L/dia) | Biogás (m³/m³) | CH₄ (%) |
|--------|----------------|----------------|---------|
| Bovino | 50 | 25 | 60% |
| Suíno | 15 | 28 | 65% |
| Avícola | 0.5 | 35 | 55% |
| Ovino | 8 | 22 | 58% |

### Fórmulas

- **Energia (kWh/dia)** = CH₄ (m³) × 9.5 kWh/m³ × 35% eficiência
- **Investimento** = Volume (m³) × Custo tipo (R$/m³) + Gerador (kW × R$ 2.500)
- **Payback** = Investimento / Lucro líquido anual
- **Crédito carbono** = MWh/ano × 0.5 ton CO₂eq/MWh × R$ 80/ton

---

## 🛠️ Instalação Local

```bash
# Clone
git clone https://github.com/Brunnobach/biogas-simulator.git
cd biogas-simulator

# Ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Dependências
pip install -r requirements.txt

# Run
python src/web/app.py
# → http://localhost:5000
```

---

## 🌐 Deploy com Cloudflare Tunnel (Recomendado)

```bash
# Instalar cloudflared
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/tunnel-guide/

# Autenticar
cloudflared tunnel login

# Criar tunnel
cloudflared tunnel create biogas-simulator

# Configurar ~/.cloudflared/config.yml
# tunnel: <UUID>
# credentials-file: ~/.cloudflared/<UUID>.json
# ingress:
#   - hostname: biogas.seudominio.com
#     service: http://localhost:5000
#   - service: http_status:404

# Run
cloudflared tunnel run biogas-simulator
```

---

## 📈 Roadmap

### Fase 1 — MVP (✅ Concluído)
- [x] Motor de cálculo técnico
- [x] Interface web responsiva
- [x] Geração de PDF
- [x] Comparativo de cenários

### Fase 2 — Monetização (Em andamento)
- [ ] Landing page de vendas
- [ ] Sistema de leads (email capture)
- [ ] Stripe/Pix para pagamentos PRO
- [ ] Analytics de uso

### Fase 3 — Escalação (Próximo)
- [ ] SEO programático (artigos técnicos auto-gerados)
- [ ] Integração com dados de mercado (CEPEA, ANP)
- [ ] API pública documentada
- [ ] White-label para cooperativas

### Fase 4 — Automação Total (Visão)
- [ ] Bot de atendimento (Ollama local)
- [ ] Newsletter automática de preços agro/energia
- [ ] Network de sites nichados (SEO programático)
- [ ] Pipeline completo: scraping → IA → publicação → monetização

---

## 💰 Modelo de Negócio

| Métrica | Valor |
|---------|-------|
| CAC estimado | R$ 0 (orgânico) |
| Ticket PRO | R$ 97/mês ou R$ 497 único |
| Target | 100 assinantes = **R$ 9.700/mês** |
| Break-even | 1 venda/mês cobre custo servidor |

### Canais de Aquisição
1. **SEO** — "calculadora biodigestor", "viabilidade biogás", "payback biodigestor"
2. **Redes sociais** — LinkedIn agronegócio, grupos de produtores rurais
3. **Parcerias** — Cooperativas, consultorias agrícolas, fornecedores de equipamentos
4. **Conteúdo** — Blog técnico com artigos auto-gerados por IA local

---

## 🤝 Contribuição

Este projeto é **open source** sob licença MIT. Contribuições são bem-vindas, especialmente:

- Melhorias no modelo de cálculo (dados reais de campo)
- Novos tipos de animais/substratos
- Traduções
- Integrações com APIs de dados agro/energia

---

## 📬 Contato

**Brunno Bachmann** — Engenheiro & Empreendedor
- 🌐 [LinkedIn](https://linkedin.com/in/brunnobachmann)
- 📧 brunnobachmann@gmail.com
- 🐦 [@brunnobachmann](https://twitter.com/brunnobachmann)

---

## 🏆 Diferenciais Competitivos

1. **Domínio técnico real** — desenvolvido por engenheiro, não apenas código
2. **Stack 100% local** — zero custos de API, privacidade total
3. **Cálculos transparentes** — todas as fórmulas documentadas
4. **Código aberto** — auditável e confiável
5. **Foco no Brasil** — parâmetros reais do mercado nacional

---

<p align="center">
  <strong>⚡ Biogas Simulator — Transformando dejetos em dinheiro.</strong><br>
  <em>Desenvolvido com Python + Ollama (Qwen 3.5) | 100% local | Zero APIs pagas</em>
</p>
