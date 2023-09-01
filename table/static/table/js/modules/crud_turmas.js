//Isso será reimplementado para salvar por pares de células
//Esse file ainda não está linkdado com o main.js

function tableToDict() {
    // Get each row data
    var rows = document.getElementById("tbl1").rows;
    var lista_turmas = [];

    for (var i = 0; i < rows.length; i++) {
        // Get each column data
        if (i == 3 || i == 7) { 
            continue;
        }

        var cols = rows[i].querySelectorAll('td');
        
        tamanho = cols.length-2
        if(i == 5){
            tamanho = cols.length
        }

        for (var j = 0; j < tamanho; j+=2) {
            // Get the text data of each cell
            var cod = cols[j].innerHTML.replace(/&nbsp;/g,"").trim();
            var prof = cols[j+1].innerHTML.replace(/&nbsp;/g,"").trim();

            // Verificar se é linha 5
            if (i == 5 && cod != "" && prof != "") {
                var disc;
                if (cod_mtr.hasOwnProperty(cod)) {
                    disc = cod_mtr[cod];
                } else if (cod_mtr_ext.hasOwnProperty(cod)) {
                    disc = cod_mtr_ext[cod];
                }

                lista_turmas.push({
                    "cod_disc" : disc,
                    "professor" : prof,
                    "horario": 2,
                    "dia": 0,
                    "cod_turma": '33'
                });
            }else if(cod != "" && prof != "") {
                var row_t = i;
                if(row_t == 4 || row_t == 5){
                    row_t = 2;
                } else if(row_t == 6){
                    row_t = 4;
                } else if(row_t == 8 || row_t == 9){
                    row_t = 5;
                } else if(row_t == 10 || row_t == 11){
                    row_t = 7;
                } else if (row_t == 1 || row_t == 2){
                    row_t--;
                }

                var disc;
                if (cod_mtr.hasOwnProperty(cod)) {
                    disc = cod_mtr[cod];
                } else if (cod_mtr_ext.hasOwnProperty(cod)) {
                    disc = cod_mtr_ext[cod];
                }

                lista_turmas.push({
                    "cod_disc" : disc,
                    "professor" : prof,
                    "horario": row_t,
                    "dia": j,
                    "cod_turma": cols[cols.length-1].innerHTML
                });
            }
        }
    }    
    sendView(lista_turmas);
}




function sendView(lista_turmas) {
    const myEvent = { 
        turmas_cadastro: lista_turmas,
        semestre: semestre,
        csrfmiddlewaretoken: '{{ csrf_token }}'
    };
    $.ajax({
        url: URL,
        type:'POST',
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        contentType: 'application/json; charset=utf-8',
        data: JSON.stringify(myEvent),
        success: function(response) {
            // Exibir o modal automaticamente com as mensagens
            if(response.conflitos_prof_semestres === "" 
            &&  response.prof_turma_extrapolando === ""){
                openModal("Salvo com sucesso!");
            }else{
                const conflitosProfSemestres = response.conflitos_prof_semestres || "\n==>sem conflitos";
                const profTurmaExtrapolando = response.prof_turma_extrapolando || "==>Sem extrapolos de creditos";

                // Concatenando as mensagens em uma única string
                var messages = "Conflitos de horário do professor:" + conflitosProfSemestres;
                messages += "\nMatéria extrapolando os créditos:\n" + profTurmaExtrapolando;

                // Abrindo o modal com as mensagens
                openModal(messages);
            }
            
        }
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}