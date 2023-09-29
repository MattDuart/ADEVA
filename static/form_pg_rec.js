django.jQuery(function () {
  console.log("iniciando");
  console.log(django.jQuery("#id_tipo").val());
  if (django.jQuery("#id_tipo").val() == "SI") {
    django.jQuery(".field-conta_origem").hide();
    django.jQuery(".field-conta_destino").show();
    django.jQuery(".field-lcto_ref").hide();
  } else if (django.jQuery("#id_tipo").val() == "TR") {
    django.jQuery(".field-conta_origem").show();
    django.jQuery(".field-conta_destino").show();
    django.jQuery(".field-lcto_ref").hide();
  } else if (django.jQuery("#id_tipo").val() == "PR") {
    django.jQuery(".field-conta_origem").hide();
    django.jQuery(".field-conta_destino").show();
    django.jQuery(".field-lcto_ref").show();
  } else {
    django.jQuery(".field-conta_origem").show();
    django.jQuery(".field-conta_destino").hide();
    django.jQuery(".field-lcto_ref").show();
  }

  django.jQuery(document).on("change", "#id_tipo", function () {
    var tipo = django.jQuery("#id_tipo").val();
    if (tipo == "SI") {
      django.jQuery(".field-conta_origem").hide();
      django.jQuery(".field-conta_destino").show();
      django.jQuery(".field-lcto_ref").hide();
    } else if (tipo == "TR") {
      django.jQuery(".field-conta_origem").show();
      django.jQuery(".field-conta_destino").show();
      django.jQuery(".field-lcto_ref").hide();
    } else if (tipo == "PG") {
      django.jQuery(".field-conta_origem").show();
      django.jQuery(".field-conta_destino").hide();
      django.jQuery(".field-lcto_ref").show();
    } else if (tipo == "PR") {
      django.jQuery(".field-conta_origem").hide();
      django.jQuery(".field-conta_destino").show();
      django.jQuery(".field-lcto_ref").show();
    }
  });
});
