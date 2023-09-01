//Carregando os dados enviados do views.py e que serão utilizados no javascript
const data = document.currentScript.dataset;
const semestre = parseInt(data.smtPagina);
URL = data.urlSave;
const dtl_profs = JSON.parse(document.getElementById("dtl_profs").textContent);
const auto_profs = JSON.parse(document.getElementById("auto_profs").textContent);
const cods_auto_ext = JSON.parse(document.getElementById("cods_auto_ext").textContent);
const cods_auto_obrig = JSON.parse(document.getElementById("cods_auto_obrig").textContent);
const mtr_auto_nome = JSON.parse(document.getElementById("mtr_auto_nome").textContent);
const restricos_hro = JSON.parse(document.getElementById("rest").textContent);

$(document).ready(function () {

    //Controla o paste para só colar texto
    document.querySelector(".editable").addEventListener("paste", function(e) {
        e.preventDefault();
        const text = e.clipboardData.getData("text/plain");
        text.trim();
        document.execCommand("insertHTML", false, text);
    });


    //Trecho para autocompletar a turma extra
    $(function() {
        // Configura o plugin Autocomplete para o input com ID "my-autocomplete-input"
        $("#mtr").autocomplete({
        source: Object.keys(mtr_auto_nome),
        minLength: 2, // Começa a exibir sugestões a partir de 2 caracteres
        
        select: function(event, ui) {
            // Função chamada quando um item é selecionado
            document.getElementById("cod").innerHTML = mtr_auto_nome[ui.item.value]
            document.getElementById("cod").style.display="block";
        }
        });
    });
    

    $(".editable td").on("dblclick", handleDoubleClick);

    function handleDoubleClick(event) {
        const cell = event.currentTarget; // A célula em que ocorreu o duplo clique
        const target = event.target; // O elemento alvo do clique dentro da célula
        let colIndex = cell.cellIndex;
        const rowIndex = cell.parentNode.rowIndex;
        const specialRows = [5, 9, 11];
        if ($.inArray(rowIndex, specialRows) !== -1) colIndex++;
        

        
        //coluna das turmas não deve ser editável
        if(colIndex == 11) return
        
        // Verifica se o alvo do clique é o ícone
        if (!target.classList.contains('fa')) editable.edit(cell, rowIndex, colIndex);
        
    }

    //exibe a caixa de mensagens para alertas
    function openModal(messages) {
        const modalBody = document.getElementById("modalBody");
        modalBody.innerText = messages;
        const myModal = new bootstrap.Modal(document.getElementById("myModal"));
        myModal.show();
    }
    
    //Lida com os detalhes do professor
    $(function() {
        $("#prof").autocomplete({
            source: function(request, response) {
                let results = $.ui.autocomplete.filter(Object.keys(auto_profs), request.term);
                response(results);
            },
            minLength: 2, // Começa a exibir sugestões a partir de 2 caracteres
            
            select: function(event, ui) {
                // Função chamada quando um item é selecionado
                // Carrega as informações de detalhes do professor 
                const nome_prof = ui.item.value.trim().toLowerCase().normalize("NFD");
                document.getElementById("nome").innerHTML = dtl_profs[nome_prof][0]|| "Sem informações";
                document.getElementById("apelido").innerHTML = dtl_profs[nome_prof][1] || "Sem informações";
                document.getElementById("pos_doc").innerHTML = dtl_profs[nome_prof][2] || "Sem informações";
                document.getElementById("pref").innerHTML = dtl_profs[nome_prof][3] || "Sem informações";
                document.getElementById("consideracao").innerHTML = dtl_profs[nome_prof][4] || "Sem informações";
                document.getElementById("infos_prof").style.display="block"; 
            }
        });
    });

    // Manipular o clique no ícone de "X" para fechar os detalhes do professor
    $('#fechar_info').click(function() {
        $('.red-transparent').removeClass('red-transparent');
        $('#prof').val("");
        $('#infos_prof').hide(); 
    });


    //Lida com os ícones de restrição
    // Variáveis de controle para o ícone
    let markCells = false;
    let transparent = false;
 
    $('#checkRestricaoHro').change(function() {
        if ($(this).is(':checked')) {
            let cells = $('#tbl1 td');
            let apelidoProf = $('#apelido').text();
            let indexes = getCellIndexes(apelidoProf);
            indexes.forEach(function (index) {
                cells.eq(index).addClass('red-transparent');
            });
            transparent = true;
        }else{
            $('.red-transparent').removeClass('red-transparent');
            transparent = false;
        }
    });

    // Função para obter índices de células das restrições de horário de um professor
    function getCellIndexes(cellName) {
        const indexes = [];
        const rest_prof = restricos_hro[cellName]
        indexes.push(...rest_prof);
        return indexes;
    }

    $('#tbl1 td').hover(function () {
        if (!markCells) {
            const cell = $(this);
            const cellText = cell.text().trim();
            const isEditable = cell.is('[contenteditable="true"]');
            let colIndex = cell[0].cellIndex;
            const rowIndex = cell.closest('tr')[0].rowIndex;
            const specialRows = [5, 9, 11];
            if ($.inArray(rowIndex, specialRows) !== -1) colIndex++;
            
            if (colIndex % 2 === 0 && cellText !== "" && !isEditable) {
                cell.find('i.fa').remove();
                cell.append('<i class="fa fa-clock-o"></i>');
            }
        }
    }, function () {
        if (!markCells) {
            $(this).find('i').remove();
        }
    });

    //Mostra a restrições quando o ícone é clicado
    $(document).on('click', '#tbl1 td i', function (e) {
        const icon = $(this);                
        markCells = !markCells;

        $('#checkRestricaoHro').prop('checked', false);
        
        if (markCells) {
            icon.removeClass('fa-clock-o').addClass('fa-check-circle');
            icon.closest('table').find('td').removeClass('red-transparent');
        
            // Adiciona a classe 'red-transparent' a células
            const cells = icon.closest('table').find('td');
            const cellContent = icon.parent().text().trim();
            const indexes = getCellIndexes(cellContent);
            
            if (indexes.length > 0) {
                indexes.forEach(function (index) {
                    cells.eq(index).addClass('red-transparent');
                });
                transparent = true;
            } else {
                 // Remove todas as mensagens flutuantes existentes
                $('.floating-message').remove();
                // Exibir mensagem flutuante
                const message = $('<div/>', {
                    class: 'floating-message',
                    text: 'Sem restrição'
                });
                const iconPosition = icon.offset();
                const iconWidth = icon.outerWidth();
                const iconHeight = icon.outerHeight();
                const messageTop = iconPosition.top + iconHeight; // Ajuste a distância vertical conforme necessário
                const messageLeft = iconPosition.left + iconWidth; // Ajuste a distância horizontal conforme necessário
                message.css({
                    top: messageTop,
                    left: messageLeft
                });
                $('body').append(message);

                // Remover a mensagem flutuante quando o mouse é movido para fora do ícone
                icon.on('mouseleave', function() {
                    message.remove();
                    cells.find('i').remove();
                });

                markCells = false;
                
            }
            
        } else {
            icon.removeClass('fa-check-circle').addClass('fa-clock-o');
            icon.closest('table').find('td').removeClass('red-transparent');
            transparent = false;
        }   
    });

   //Manipula o processo de edição das células
    const editable = {
        icon: null,
        rowIndex: 0,
        colIndex: 0,
        selected : null, // current selected cell
        value : "", // current selected cell value
        // (B) "CONVERT" TO EDITABLE CELL
        edit: (cell, row, col) => {

            $('#checkRestricaoHro').prop('checked', false);

            editable.rowIndex = row;
            editable.colIndex = col;
            // Remove ícone presente na célula
            let table = $('#tbl1');
            table.find('i').remove();
            
            // Remove a classe 'red-transparent' das células marcadas
            if(transparent){
                $(cell).closest('table').find('td.red-transparent').removeClass('red-transparent');
                markCells = !markCells;
                transparent = false;
            }
                        
            
            // (B1) REMOVE "DOUBLE CLICK TO EDIT"
            cell.ondblclick = "";

            // (B2) EDITABLE CONTENT
            $(cell).attr("contenteditable", "true");
            $(cell).focus();
            
            // (B2.1) ADD AUTOCOMPLETE
            if (col % 2 === 0){
                //autocompleta com o nome do professor
                $(cell).autocomplete({
                    source: function(request, response) {
                        const results = $.ui.autocomplete.filter(Object.keys(auto_profs), request.term);
                        response(results.slice(0, 3));
                    },
                    minLength: 2,
                    select: function(event, ui) {
                        const nomeProf = ui.item.value;
                        const apelidoProf = auto_profs[nomeProf];
                        $(cell).html(apelidoProf);
                        return false;
                    }
                }).focus(function() {
                    $(this).autocomplete("search");
                });    
            }else {
                //autocompleta com a matéria
                $(cell).autocomplete({
                    source: function(request, response) {
                        let results;
                        //linhas entre [4,6] são do vespertino
                        if (row >= 4 && row <= 6) {
                            results = $.ui.autocomplete.filter(Object.keys(cods_auto_obrig).concat(Object.keys(cods_auto_ext)), request.term);
                        } else {
                            results = $.ui.autocomplete.filter(Object.keys(cods_auto_obrig), request.term);
                        }
                        response(results.slice(0, 4));
                    },
                    minLength: 2,
                    select: function(event, ui) {
                        $(cell).html(ui.item.value);
                        return false;
                    }
                }).focus(function() {
                    $(this).autocomplete("search");
                });
                
            }

            // (C3) "MARK" CURRENT SELECTED CELL
            cell.classList.add("edit");
            editable.selected = cell;
            editable.value = cell.innerHTML;
        
            // (C4) PRESS ENTER/ESC OR CLICK OUTSIDE TO END EDIT
            window.addEventListener("click", editable.close);
            cell.onkeydown = evt => {
                if (evt.key=="Enter" || evt.key=="Escape") {
                    editable.close(evt.key=="Enter" ? true : false);
                    return false;
                }
            };

        },

        // (C) END "EDIT MODE"
        close: evt => {
            if (evt.target !== editable.selected) {

                const user = editable.selected.innerHTML;
                const valueUser = user.replace(/&nbsp;/g, '');
                const col = editable.colIndex;
                const row = editable.rowIndex;
                valueUser.trim();    

                if (col % 2 !== 0 && valueUser !== "") {
                    let ExistMtr = false;
                    if (cods_auto_obrig.hasOwnProperty(valueUser)) ExistMtr = true;

                    if(row >= 4 && row <= 6 && cods_auto_ext.hasOwnProperty(valueUser))  ExistMtr = true; 
                    
                    if (!ExistMtr) {
                        editable.selected.innerHTML = "";
                        openModal("Matéria de código inválido! Consulte os valores na tabela.");
                    }
                }else if(valueUser !== ""){
                    let ExistProf = false;

                    const nomeEncontrado = Object.keys(auto_profs).find(function(nome) {
                        return auto_profs[nome] === valueUser;
                    });
                      
                    if (nomeEncontrado) { ExistProf = true }
                    
                    if(!ExistProf){
                        openModal("Nome do professor incorreto.");
                        editable.selected.innerHTML = "";
                    }
                }
        

                // (C2) REMOVE "EDITABLE"
                window.getSelection().removeAllRanges();
                editable.selected.contentEditable = false;

                // (C3) RESTORE CLICK LISTENERS
                window.removeEventListener("click", editable.close);

                // (C4) "UNMARK" CURRENT SELECTED CELL
                editable.selected.classList.remove("edit");
                editable.selected = null;

            }
        }
    };
});


