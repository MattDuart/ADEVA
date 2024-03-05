document.addEventListener("DOMContentLoaded", function () {
  // Localiza o elemento inline-group
  var inlineGroup = document.querySelector("#lcto_detalhe-group");

  // Localiza o elemento field-especie
  var fieldEspecie = document.querySelector(".form-row.field-item_orcamento");

  // Move o inline-group para depois do field-especie
  if (fieldEspecie && inlineGroup) {
    fieldEspecie.parentNode.insertBefore(inlineGroup, fieldEspecie.nextSibling);
  }

  var inlineGroup2 = document.querySelector("#lcto_arquivos-group");

  // Localiza o elemento field-especie
  var fieldEspecie2 = document.querySelector(".form-row.field-image");

  // Move o inline-group para depois do field-especie
  if (fieldEspecie2 && inlineGroup2) {
    fieldEspecie2.parentNode.insertBefore(
      inlineGroup2,
      fieldEspecie2.nextSibling
    );

    // Localiza o elemento field-especie
    var valor = document.querySelector(".form-row.field-valor_docto");

    // Move o inline-group para depois do field-especie
    if (valor && inlineGroup) {
      inlineGroup.parentNode.insertBefore(valor, inlineGroup.nextSibling);
    }
  }

  var valorDoctoDiv = document.querySelector(
    ".form-row.field-valor_docto .readonly"
  );

  // Função para atualizar a soma
  function atualizarSoma() {
    var soma = 0;
    var numberInputs = inlineGroup.querySelectorAll(
      'table input[type="number"]'
    );

    numberInputs.forEach(function (input) {
      var valor = parseFloat(input.value) || 0;
      soma += valor;
    });

    valorDoctoDiv.textContent = soma.toFixed(2); // Atualiza a soma na div readonly
  }
  atualizarSoma();

  if (inlineGroup && valorDoctoDiv) {
    // Adiciona um ouvinte para qualquer mudança de foco na página
    document.addEventListener("focusout", function (event) {
      if (event.target.matches('table input[type="number"]')) {
        atualizarSoma();
      }
    });
  }
});
