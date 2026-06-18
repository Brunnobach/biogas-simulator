/**
 * Biogas Simulator - Frontend Application
 * Handles simulation, visualization, and PDF generation
 */

// API endpoint
const API_BASE = window.location.origin;

// DOM Elements
const elements = {
    animalType: document.getElementById('animal_type'),
    numAnimals: document.getElementById('num_animals'),
    digesterType: document.getElementById('digester_type'),
    locationState: document.getElementById('location_state'),
    eletricityCost: document.getElementById('eletricity_cost'),
    hasGenerator: document.getElementById('has_generator'),
    generatorPower: document.getElementById('generator_power'),
    generatorPowerGroup: document.getElementById('generator_power_group'),
    useCreditCarbono: document.getElementById('use_credit_carbono'),
    results: document.getElementById('results'),
    viabilityBadge: document.getElementById('viability-badge'),
    leadEmail: document.getElementById('lead_email'),
};

// State
let currentResult = null;

// Event Listeners
elements.hasGenerator.addEventListener('change', (e) => {
    elements.generatorPowerGroup.style.display = e.target.checked ? 'block' : 'none';
});

// Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Format number
function formatNumber(value, decimals = 1) {
    return new Intl.NumberFormat('pt-BR', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(value);
}

// Run simulation
async function runSimulation() {
    const btn = document.querySelector('.btn-simulate');
    btn.innerHTML = '<span class="loading"></span> Calculando...';
    btn.disabled = true;

    const params = {
        animal_type: elements.animalType.value,
        num_animals: parseInt(elements.numAnimals.value),
        digester_type: elements.digesterType.value,
        location_state: elements.locationState.value,
        eletricity_cost_kwh: parseFloat(elements.eletricityCost.value) || 0,
        has_generator: elements.hasGenerator.checked,
        generator_power_kw: parseFloat(elements.generatorPower.value) || 0,
        use_credit_carbono: elements.useCreditCarbono.checked
    };

    try {
        const response = await fetch(`${API_BASE}/api/simulate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });

        if (!response.ok) throw new Error('Erro na simulação');

        const result = await response.json();
        currentResult = result;
        displayResults(result);

    } catch (error) {
        alert('Erro ao executar simulação: ' + error.message);
        console.error(error);
    } finally {
        btn.innerHTML = '<span class="btn-icon">▶</span> Simular Viabilidade';
        btn.disabled = false;
    }
}

// Display results
function displayResults(result) {
    elements.results.style.display = 'block';
    elements.results.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Viability badge
    elements.viabilityBadge.textContent = result.viavel ? 'VIÁVEL' : 'NÃO VIÁVEL';
    elements.viabilityBadge.className = `viability-badge ${result.viavel ? 'viable' : 'not-viable'}`;

    // KPIs
    document.getElementById('kpi-invest').textContent = formatCurrency(result.investimento_total);
    document.getElementById('kpi-payback').textContent = 
        result.payback_years === Infinity ? 'N/A' : `${formatNumber(result.payback_years, 1)} anos`;
    document.getElementById('kpi-roi').textContent = `${formatNumber(result.roi_annual, 1)}%`;
    document.getElementById('kpi-energy').textContent = `${formatNumber(result.potential_energy_kwh_day, 1)} kWh`;

    // Energy bars
    const maxEnergy = Math.max(
        result.potential_energy_kwh_day,
        result.potential_energy_kwh_month / 30,
        result.potential_energy_kwh_year / 365
    );

    document.getElementById('bar-daily').style.width = `${(result.potential_energy_kwh_day / maxEnergy) * 100}%`;
    document.getElementById('bar-daily-val').textContent = `${formatNumber(result.potential_energy_kwh_day, 1)} kWh`;

    document.getElementById('bar-monthly').style.width = `${((result.potential_energy_kwh_month / 30) / maxEnergy) * 100}%`;
    document.getElementById('bar-monthly-val').textContent = `${formatNumber(result.potential_energy_kwh_month, 0)} kWh`;

    document.getElementById('bar-yearly').style.width = `${((result.potential_energy_kwh_year / 365) / maxEnergy) * 100}%`;
    document.getElementById('bar-yearly-val').textContent = `${formatNumber(result.potential_energy_kwh_year, 0)} kWh`;

    // Financial
    document.getElementById('fin-eco-mes').textContent = formatCurrency(result.economia_mensal_eletricidade);
    document.getElementById('fin-eco-ano').textContent = formatCurrency(result.economia_anual_eletricidade);
    document.getElementById('fin-co2').textContent = `${formatNumber(result.credito_carbono_anual, 1)} ton`;
    document.getElementById('fin-carbono-val').textContent = formatCurrency(result.credito_carbono_valor_anual);
    document.getElementById('fin-receita').textContent = formatCurrency(result.receita_total_anual);
    document.getElementById('fin-lucro').textContent = formatCurrency(result.lucro_liquido_anual);
    document.getElementById('fin-vpl').textContent = formatCurrency(result.vpl_10anos);

    // Production
    document.getElementById('prod-dejeto').textContent = `${formatNumber(result.daily_dejeto_m3, 2)} m³`;
    document.getElementById('prod-biogas').textContent = `${formatNumber(result.daily_biogas_m3, 1)} m³`;
    document.getElementById('prod-ch4').textContent = `${formatNumber(result.daily_ch4_m3, 1)} m³`;

    // Scenarios table
    const tbody = document.getElementById('scenarios-tbody');
    tbody.innerHTML = '';
    result.cenarios.forEach(cenario => {
        const row = document.createElement('tr');
        const viavelClass = cenario.viavel ? 'scenario-viable' : 'scenario-not-viable';
        const viavelText = cenario.viavel ? 'VIÁVEL' : 'NÃO VIÁVEL';
        row.innerHTML = `
            <td><strong>${capitalize(cenario.tipo)}</strong></td>
            <td>${formatCurrency(cenario.investimento)}</td>
            <td>${formatNumber(cenario.payback_anos, 1)} anos</td>
            <td>${formatNumber(cenario.roi, 0)}%</td>
            <td class="${viavelClass}">${viavelText}</td>
        `;
        tbody.appendChild(row);
    });

    // Recommendations
    const recList = document.getElementById('recommendations-list');
    recList.innerHTML = '';
    if (result.recomendacoes && result.recomendacoes.length > 0) {
        result.recomendacoes.forEach(rec => {
            const li = document.createElement('li');
            li.textContent = rec;
            recList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'Consulte um engenheiro especializado para análise detalhada do seu projeto.';
        recList.appendChild(li);
    }
}

// Capitalize string
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Generate PDF
async function generatePDF() {
    const email = elements.leadEmail.value.trim();
    if (!email || !email.includes('@')) {
        alert('Por favor, insira um email válido para receber o relatório.');
        return;
    }

    if (!currentResult) {
        alert('Execute uma simulação primeiro.');
        return;
    }

    const btn = document.querySelector('.btn-cta');
    btn.innerHTML = '<span class="loading"></span> Gerando PDF...';
    btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/api/pdf`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: email,
                simulation: currentResult
            })
        });

        if (!response.ok) throw new Error('Erro ao gerar PDF');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `relatorio-biogas-${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        alert('Relatório PDF gerado com sucesso! Verifique seus downloads.');

    } catch (error) {
        alert('Erro ao gerar PDF: ' + error.message);
        console.error(error);
    } finally {
        btn.innerHTML = '📄 Gerar Relatório PDF';
        btn.disabled = false;
    }
}

// Auto-simulate on load with default values
window.addEventListener('load', () => {
    // Pre-fill with reasonable defaults
    setTimeout(() => {
        // Optional: auto-run on first visit
        // runSimulation();
    }, 500);
});
