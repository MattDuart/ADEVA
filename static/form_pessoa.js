django.jQuery(function () {
  // para iniciar sempre com pagamento
  django.jQuery("#pessoasfisicas-group").hide();
  django.jQuery("pessoasjuridicas-group").show();

  django.jQuery(document).on("change", "#id_tipo", function () {
    var tipo = django.jQuery("#id_tipo").val();
    if (tipo == "J") {
      django.jQuery("#pessoasfisicas-group").hide();
      django.jQuery("pessoasjuridicas-group").show();
    } else if (tipo == "F") {
      django.jQuery("#pessoasfisicas-group").show();
      django.jQuery("pessoasjuridicas-group").hide();
    }
  });
});
