
const auto_profs = JSON.parse(document.getElementById("auto_profs").textContent);

$(document).ready(function() {
    $(".icone").mouseover(function() {
        $(this).css("color", "blue");
    });

    $(".icone").mouseout(function() {
        $(this).css("color", "");
    });

    //Abre popUp
    $(document).on('click', '.icone', function (e) {              
        const cell = $(this).closest('td');
        const row = cell.closest('tr');

        //carrega o nome no popup
        $("#prof_rp1, #prof_rp3, #prof_rp2").val("");
        
        let count = 1;
        row.find('.n_completo').each(function(){
            const id = "#prof_rp" + count;
            $(id).val($(this).text().trim());
            count++;
        });
        count = 1;

        $("#popup").show();
        $("#submitForm").off("click").on("click", function(){
            controlaPopUp(cell.prev(), auto_profs);
        });
    });

    $(function() {
        $("#prof_rp1, #prof_rp2, #prof_rp3").autocomplete({
            source: function(request, response) {
                let results = $.ui.autocomplete.filter(Object.keys(auto_profs), request.term);
                response(results);
            },
            minLength: 2
        })
    });

    
   
    $("#closePopup").on("click", function(){
        $("#popup").hide()
    })

    function controlaPopUp(cell, apelidos){

        let resposta = {};
        const campo1Value = document.querySelector(".campo1").value;
        const campo2Value = document.querySelector(".campo2").value;
        const campo3Value = document.querySelector(".campo3").value;

        resposta = {
            professor1: campo1Value,
            professor2: campo2Value,
            professor3: campo3Value,
        }
        
        campo1Value ? resposta.professor1 = apelidos[resposta.professor1] : ""
        campo2Value ? resposta.professor2 = apelidos[resposta.professor2] : ""
        campo3Value ? resposta.professor3 = apelidos[resposta.professor3] : ""

        
        let resp = []
        if(resposta.professor1 != "") resp.push(resposta.professor1)
        if(resposta.professor2 != "") resp.push(resposta.professor2)
        if(resposta.professor3 != "") resp.push(resposta.professor3)

        //valida nomes
        let validInput = true;
        const lProfs = [campo1Value, campo2Value, campo3Value];

        for (let i = 0; i < lProfs.length; i++) {
            let nomeEncontrado = false;
            const idAlerta = "#" + i;

            $(idAlerta).hide()
            if (auto_profs.hasOwnProperty(lProfs[i])) nomeEncontrado = true;
            if(lProfs[i] === "") nomeEncontrado = true;

            if (!nomeEncontrado) {
                $(idAlerta).html("Nome inválido");
                $(idAlerta).css("color", "red");
                $(idAlerta).css("font-size", "12px");
                $(idAlerta).show()
                validInput = false;
                break;
            }               
        }

        if(validInput){
            const myEvent = { 
                id: $(cell).prev().text(),
                lProfs: lProfs,
                csrfmiddlewaretoken: window.CSRF_TOKEN
            };
    
            $.ajax({
                url: $("#url-data").data("url"),
                type: "POST",
                dataType: "json",
                data: JSON.stringify(myEvent),
                headers: {
                  "X-Requested-With": "XMLHttpRequest",
                  "X-CSRFToken": getCookie("csrftoken"), 
                },
                success: (data) => {
                    
                },
                error: (error) => {
                    alert("Ocorreu um erro ao manipular as informações");
                }
            });

            const row = cell.closest('tr');
            row.find('.n_completo').remove();
            lProfs.forEach(nome => {
                row.append('<td class="d-none n_completo">'+nome+'</td>')
            });
            $("#popup").hide();
            cell.html(resp.join(","));
        }
    }
});

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