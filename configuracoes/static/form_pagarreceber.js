django.jQuery(function () {
  // para iniciar sempre com pagamento
  console.log("iniciando");
  django.jQuery(".field-numero_banco").hide();
  django.jQuery(".field-nome_banco").hide();
  django.jQuery(".field-numero_agencia").hide();
  django.jQuery(".field-digito_agencia").hide();
  django.jQuery(".field-numero_conta").hide();
  django.jQuery(".field-chave_pix").hide();
  django.jQuery(".field-digito_conta").hide();
  django.jQuery(".field-tipo").hide();
  django.jQuery(".field-favorecido").hide();

  django.jQuery(document).on("change", "#id_bancaria", function () {
    var bancaria = django.jQuery("#id_bancaria");

    if (bancaria.is(":checked")) {
      django.jQuery(".field-numero_banco").show();
      django.jQuery(".field-nome_banco").show();
      django.jQuery(".field-numero_agencia").show();
      django.jQuery(".field-digito_agencia").show();
      django.jQuery(".field-numero_conta").show();
      django.jQuery(".field-chave_pix").show();
      django.jQuery(".field-digito_conta").show();
      django.jQuery(".field-tipo").show();
      django.jQuery(".field-favorecido").show();
    } else {
      django.jQuery(".field-numero_banco").hide();
      django.jQuery(".field-nome_banco").hide();
      django.jQuery(".field-numero_agencia").hide();
      django.jQuery(".field-digito_agencia").hide();
      django.jQuery(".field-numero_conta").hide();
      django.jQuery(".field-chave_pix").hide();
      django.jQuery(".field-digito_conta").hide();
      django.jQuery(".field-tipo").hide();
      django.jQuery(".field-favorecido").hide();
    }
  });
});
