"""
Biogas Simulator Engine v1.0
Cálculos de viabilidade econômica de biodigestores
Baseado em parâmetros técnicos reais do setor agroenergia
"""

import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from enum import Enum

class AnimalType(Enum):
    BOVINO = "bovino"
    SUINO = "suino"
    AVICOLA = "avícola"
    OVINO = "ovino"

class DigesterType(Enum):
    CHINESE = "chinese"  # Batelada
    INDIAN = "indian"    # Fluxo contínuo
    COBERTURA = "cobertura"  # Biodigestor de lagoa
    TUBULAR = "tubular"  # Modelo canadiense

@dataclass
class SimulationInput:
    """Entrada do usuário para simulação"""
    animal_type: AnimalType
    num_animals: int
    digester_type: DigesterType
    location_state: str  # UF
    eletricity_cost_kwh: float  # R$/kWh
    has_generator: bool = False
    generator_power_kw: float = 0.0
    use_credit_carbono: bool = False
    
@dataclass
class SimulationResult:
    """Resultado completo da simulação"""
    # Produção
    daily_dejeto_m3: float
    daily_biogas_m3: float
    daily_ch4_m3: float
    
    # Energia
    potential_energy_kwh_day: float
    potential_energy_kwh_month: float
    potential_energy_kwh_year: float
    
    # Financeiro
    investimento_total: float
    payback_years: float
    payback_months: float
    roi_annual: float
    
    # Economia
    economia_mensal_eletricidade: float
    economia_anual_eletricidade: float
    
    # Crédito carbono
    credito_carbono_anual: float
    credito_carbono_valor_anual: float
    
    # Receita total
    receita_total_anual: float
    lucro_liquido_anual: float
    
    # Indicadores
    vpl_10anos: float
    tir_percent: float
    
    # Recomendações
    viavel: bool
    recomendacoes: List[str]

# === CONSTANTES TÉCNICAS ===

# Produção de dejetos por animal (m³/dia)
DEJETO_PRODUCAO = {
    AnimalType.BOVINO: 0.050,      # 50L/dia por cabeça
    AnimalType.SUINO: 0.015,       # 15L/dia por cabeça
    AnimalType.AVICOLA: 0.0005,    # 0.5L/dia por ave
    AnimalType.OVINO: 0.008,       # 8L/dia por cabeça
}

# Potencial de produção de biogás (m³ biogas/m³ dejetos)
BIOGAS_POTENCIAL = {
    AnimalType.BOVINO: 25.0,
    AnimalType.SUINO: 28.0,
    AnimalType.AVICOLA: 35.0,
    AnimalType.OVINO: 22.0,
}

# Teor de CH4 no biogas (%)
CH4_TEOR = {
    AnimalType.BOVINO: 0.60,
    AnimalType.SUINO: 0.65,
    AnimalType.AVICOLA: 0.55,
    AnimalType.OVINO: 0.58,
}

# Poder calorífico do CH4: 9.5 kWh/m³
PODER_CALORIFICO_CH4 = 9.5

# Eficiência de conversão para eletricidade
EFICIENCIA_GERACAO = 0.35  # 35% motor gerador

# Custo de implementação por m³ de biodigestor (R$)
CUSTO_IMPLANTACAO_M3 = {
    DigesterType.CHINESE: 800.0,
    DigesterType.INDIAN: 1200.0,
    DigesterType.COBERTURA: 400.0,
    DigesterType.TUBULAR: 600.0,
}

# Custo operacional anual (% do investimento)
CUSTO_OPERACIONAL_ANUAL_PCT = 0.05

# Preço crédito carbono (R$/ton CO2eq)
PRECO_CREDITO_CARBONO = 80.0

# Fator de emissão evitada (ton CO2eq/MWh)
FATOR_EMISSAO_EVITADA = 0.5

# Tarifas médias de energia por estado (R$/kWh) - atualizar periodicamente
TARIFAS_ENERGIA = {
    "SP": 0.85, "RJ": 0.92, "MG": 0.78, "PR": 0.72, "SC": 0.70,
    "RS": 0.75, "GO": 0.68, "MT": 0.65, "MS": 0.70, "BA": 0.80,
    "PE": 0.88, "CE": 0.90, "MA": 0.95, "PA": 0.85, "TO": 0.72,
    "RO": 0.75, "AC": 0.92, "AM": 0.95, "RR": 1.00, "AP": 0.90,
    "PB": 0.88, "RN": 0.90, "AL": 0.92, "SE": 0.88, "PI": 0.90,
    "DF": 0.80, "ES": 0.85,
}

class BiogasSimulator:
    """Motor de simulação de viabilidade de biodigestores"""
    
    def __init__(self):
        self.version = "1.0.0"
    
    def simulate(self, input_data: SimulationInput) -> SimulationResult:
        """Executa simulação completa"""
        
        # === CÁLCULOS DE PRODUÇÃO ===
        daily_dejeto = input_data.num_animals * DEJETO_PRODUCAO[input_data.animal_type]
        biogas_potencial = BIOGAS_POTENCIAL[input_data.animal_type]
        daily_biogas = daily_dejeto * biogas_potencial
        daily_ch4 = daily_biogas * CH4_TEOR[input_data.animal_type]
        
        # === CÁLCULOS DE ENERGIA ===
        energy_kwh_day = daily_ch4 * PODER_CALORIFICO_CH4 * EFICIENCIA_GERACAO
        energy_kwh_month = energy_kwh_day * 30
        energy_kwh_year = energy_kwh_day * 365
        
        # === CÁLCULOS FINANCEIROS ===
        # Volume do biodigestor (dias de retenção)
        dias_retencao = {
            DigesterType.CHINESE: 30,
            DigesterType.INDIAN: 20,
            DigesterType.COBERTURA: 45,
            DigesterType.TUBULAR: 25,
        }
        volume_digester = daily_dejeto * dias_retencao[input_data.digester_type]
        
        # Investimento
        custo_por_m3 = CUSTO_IMPLANTACAO_M3[input_data.digester_type]
        investimento = volume_digester * custo_por_m3
        
        # Adicionar gerador se necessário
        if input_data.has_generator and input_data.generator_power_kw > 0:
            investimento += input_data.generator_power_kw * 2500  # R$ 2.500/kW
        
        # Custos operacionais
        custo_operacional_anual = investimento * CUSTO_OPERACIONAL_ANUAL_PCT
        
        # === ECONOMIA ===
        tarifa = input_data.eletricity_cost_kwh or TARIFAS_ENERGIA.get(input_data.location_state, 0.80)
        economia_mensal = energy_kwh_month * tarifa
        economia_anual = economia_mensal * 12
        
        # === CRÉDITO CARBONO ===
        credito_carbono_anual = 0.0
        credito_carbono_valor = 0.0
        if input_data.use_credit_carbono:
            mwh_ano = energy_kwh_year / 1000
            ton_co2 = mwh_ano * FATOR_EMISSAO_EVITADA
            credito_carbono_anual = ton_co2
            credito_carbono_valor = ton_co2 * PRECO_CREDITO_CARBONO
        
        # === RECEITA TOTAL ===
        receita_total = economia_anual + credito_carbono_valor
        lucro_liquido = receita_total - custo_operacional_anual
        
        # === PAYBACK ===
        if lucro_liquido > 0:
            payback_years = investimento / lucro_liquido
            payback_months = payback_years * 12
        else:
            payback_years = float('inf')
            payback_months = float('inf')
        
        # === ROI ===
        roi = (lucro_liquido / investimento) * 100 if investimento > 0 else 0
        
        # === VPL e TIR (simplificado) ===
        taxa_desconto = 0.10  # 10% aa
        vpl = -investimento
        for ano in range(1, 11):
            vpl += lucro_liquido / ((1 + taxa_desconto) ** ano)
        
        # TIR simplificada (aproximação)
        tir = roi if vpl > 0 else 0
        
        # === VIABILIDADE ===
        viavel = payback_years < 7 and vpl > 0 and roi > 10
        
        # === RECOMENDAÇÕES ===
        recomendacoes = []
        if payback_years > 10:
            recomendacoes.append("Payback superior a 10 anos. Considere aumentar escala ou buscar subsídios.")
        elif payback_years < 3:
            recomendacoes.append("Excelente viabilidade! Payback inferior a 3 anos.")
        
        if input_data.num_animals < 50 and input_data.animal_type == AnimalType.BOVINO:
            recomendacoes.append("Para rebanhos pequenos, considere biodigestor de cobertura (menor investimento).")
        
        if not input_data.has_generator:
            recomendacoes.append("Adicionar gerador pode aumentar receita com venda de energia ou substituição total da conta.")
        
        if input_data.use_credit_carbono and credito_carbono_valor > 0:
            recomendacoes.append(f"Crédito de carbono pode gerar R$ {credito_carbono_valor:,.2f}/ano adicionais.")
        
        if energy_kwh_year > 100000:
            recomendacoes.append("Produção energética significativa. Avalie venda para rede via net metering.")
        
        return SimulationResult(
            daily_dejeto_m3=daily_dejeto,
            daily_biogas_m3=daily_biogas,
            daily_ch4_m3=daily_ch4,
            potential_energy_kwh_day=energy_kwh_day,
            potential_energy_kwh_month=energy_kwh_month,
            potential_energy_kwh_year=energy_kwh_year,
            investimento_total=investimento,
            payback_years=payback_years,
            payback_months=payback_months,
            roi_annual=roi,
            economia_mensal_eletricidade=economia_mensal,
            economia_anual_eletricidade=economia_anual,
            credito_carbono_anual=credito_carbono_anual,
            credito_carbono_valor_anual=credito_carbono_valor,
            receita_total_anual=receita_total,
            lucro_liquido_anual=lucro_liquido,
            vpl_10anos=vpl,
            tir_percent=tir,
            viavel=viavel,
            recomendacoes=recomendacoes
        )
    
    def get_scenario_comparison(self, input_data: SimulationInput) -> List[Dict]:
        """Compara diferentes tipos de biodigestor para o mesmo cenário"""
        scenarios = []
        for digester in DigesterType:
            input_copy = SimulationInput(
                animal_type=input_data.animal_type,
                num_animals=input_data.num_animals,
                digester_type=digester,
                location_state=input_data.location_state,
                eletricity_cost_kwh=input_data.eletricity_cost_kwh,
                has_generator=input_data.has_generator,
                generator_power_kw=input_data.generator_power_kw,
                use_credit_carbono=input_data.use_credit_carbono
            )
            result = self.simulate(input_copy)
            scenarios.append({
                "tipo": digester.value,
                "investimento": result.investimento_total,
                "payback_anos": result.payback_years,
                "roi": result.roi_annual,
                "viavel": result.viavel,
                "receita_anual": result.receita_total_anual
            })
        return scenarios

# === FUNÇÃO DE CONVENIÊNCIA ===

def run_simulation(
    animal_type: str,
    num_animals: int,
    digester_type: str,
    location_state: str,
    eletricity_cost_kwh: float = 0.0,
    has_generator: bool = False,
    generator_power_kw: float = 0,
    use_credit_carbono: bool = False
) -> Dict:
    """Executa simulação e retorna resultado como dict"""
    simulator = BiogasSimulator()
    
    input_data = SimulationInput(
        animal_type=AnimalType(animal_type),
        num_animals=num_animals,
        digester_type=DigesterType(digester_type),
        location_state=location_state.upper(),
        eletricity_cost_kwh=eletricity_cost_kwh or TARIFAS_ENERGIA.get(location_state.upper(), 0.80),
        has_generator=has_generator,
        generator_power_kw=generator_power_kw,
        use_credit_carbono=use_credit_carbono
    )
    
    result = simulator.simulate(input_data)
    
    # Converter para dict serializável
    result_dict = asdict(result)
    result_dict["recomendacoes"] = result.recomendacoes
    
    # Adicionar cenários comparativos
    result_dict["cenarios"] = simulator.get_scenario_comparison(input_data)
    
    return result_dict


if __name__ == "__main__":
    # Teste rápido
    print("=== TESTE: Fazenda com 100 bovinos em MG ===")
    result = run_simulation(
        animal_type="bovino",
        num_animals=100,
        digester_type="chinese",
        location_state="MG",
        has_generator=True,
        generator_power_kw=50,
        use_credit_carbono=True
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
