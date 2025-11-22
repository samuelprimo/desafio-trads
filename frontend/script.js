const faixasSelecionadas = [];

function adicionarIdade() {
    const select = document.getElementById('nova-idade');
    const valor = select.value;
    faixasSelecionadas.push(valor);
    atualizarListaIdades();
}

function removerIdade(index) {
    faixasSelecionadas.splice(index, 1);
    atualizarListaIdades();
}

function atualizarListaIdades() {
    const container = document.getElementById('lista-idades');
    container.innerHTML = '';
    faixasSelecionadas.forEach((faixa, index) => {
        container.innerHTML += `
            <span class="tag-idade">
                ${faixa} <span onclick="removerIdade(${index})" style="cursor:pointer; margin-left:5px;">&times;</span>
            </span>
        `;
    });
    document.getElementById('vidas').value = faixasSelecionadas.length || 1;
}

document.getElementById('cotacaoForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (faixasSelecionadas.length === 0) {
        alert("Necessário selecionar ao menos uma faixa etária.");
        return;
    }

    document.getElementById('loading').classList.remove('d-none');
    document.getElementById('resultados-area').classList.add('d-none');
    document.getElementById('empty-state').classList.add('d-none');

    const payload = {
        vidas: parseInt(document.getElementById('vidas').value),
        faixas_etarias: faixasSelecionadas,
        estado: document.getElementById('estado').value || null
    };

    try {
        const response = await fetch('http://localhost:5000/api/cotacao', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        renderizarResultados(data);

    } catch (error) {
        console.error(error);
        alert("Erro de comunicação com o servidor.");
    } finally {
        document.getElementById('loading').classList.add('d-none');
        document.getElementById('resultados-area').classList.remove('d-none');
    }
});

function renderizarResultados(data) {
    const containerRec = document.getElementById('lista-recomendados');
    const containerGeral = document.getElementById('lista-geral');
    containerRec.innerHTML = '';
    containerGeral.innerHTML = '';

    if (!data.planos || data.planos.length === 0) {
        containerGeral.innerHTML = '<div class="alert alert-warning">Nenhum registro encontrado.</div>';
        return;
    }

    data.planos.forEach(plano => {
        const isRecomendado = plano.recomendado;
        const scorePct = Math.round(plano.score_recomendacao * 100);
        
        const cardHtml = `
            <div class="card mb-2 card-plano ${isRecomendado ? 'recomendado-border' : 'border-light'}">
                <div class="card-body py-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            ${isRecomendado ? `<span class="badge bg-success mb-2">compatibilidade: ${scorePct}%</span>` : ''}
                            <h6 class="card-title fw-bold text-dark mb-1">${plano.plano}</h6>
                            <p class="text-secondary small mb-1">Ref: ${plano.plano_id} | ${plano.estado}</p>
                            <div>
                                <span class="badge bg-light text-dark border fw-normal">${plano.acomodacao}</span>
                                <span class="badge bg-light text-dark border fw-normal">${plano.coparticipacao}</span>
                            </div>
                        </div>
                        <div class="text-end">
                            <small class="text-secondary d-block">Mensalidade</small>
                            <h4 class="text-success fw-bold">R$ ${plano.valor_total.toFixed(2)}</h4>
                        </div>
                    </div>
                </div>
            </div>
        `;

        if (isRecomendado) {
            containerRec.innerHTML += cardHtml;
        } else {
            containerGeral.innerHTML += cardHtml;
        }
    });
    
    if (containerRec.innerHTML === '') {
        containerRec.innerHTML = '<p class="text-muted small">nenhuma recomendação específica para este perfil.</p>';
    }
}