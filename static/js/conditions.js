
<script>
    $(document).ready(function() {
                        $("#submit_btn").hide();
        $("#submit_btn").attr("disabled", true);;
        $("#value_div_bidding").hide();
             $("#value_div_advertising").hide();
             $("#value_div_matchtype").hide();
             $("#value_div_number").hide();
             $("#value_div_string").hide();
        $("#select_scope").hide();
        $("#date_range").hide();
        $("#attributes_div").hide();

        $("#attribute_operand").click(function(event) {
            $("#select_scope").show();
                    $("#date_range").show();
                    $("#submit_btn").show();

            $("#attributes_div").show();
            $("#operations_div_string").hide();
            $("#operations_div_number").hide();
            $("#operations_div_label").hide();
             $("#value_div_bidding").hide();
             $("#value_div_advertising").hide();
             $("#value_div_matchtype").hide();
             $("#value_div_number").hide();
             $("#value_div_string").hide();
        });

        $("#value_operand").click(function(event) {
            $("#attributes_div").hide();



            $("#operations_div_string").hide();
            $("#operations_div_number").hide();
            $("#operations_div_label").hide();

           if ($("#attribute_operand").attr('tagvalue')=='BiddingStrategyType')
           {
            $("#value_div_bidding").show();
           }
           else if ($("#attribute_operand").attr('tagvalue')=='AdvertisingChannelType')
           {
            $("#value_div_advertising").show();
           }
           else if ($("#attribute_operand").attr('tagvalue')=='KeywordMatchType')
           {
            $("#value_div_matchtype").show();
           }
           else if ($("#attribute_operand").attr('value')=='number')
           {
            $("#value_div_number").show();
           }
           else if ($("#attribute_operand").attr('value')=='string')
           {
               $("#value_div_string").show();
           }
           else if ($("#attribute_operand").attr('value')=='label')
           {
               $("#value_div_string").show();
           }

        });

        $("#attributes_div").on('click', '.field_btn', function() {

            $("#attribute_operand").text($(this).text());
            $("#attribute_operand").attr('tagvalue',$(this).attr('tagvalue'))
            $("#attribute_operand").val($(this).val());
            $("#attribute_operation").val($(this).val());
            $("#attribute_operation").text('operation');



        });
          $("#value_div_bidding").on('click', '.values_btn', function() {

            $("#value_operand").text($(this).text());
            $("#value_operand").attr('value',$(this).attr('value'))
                    $("#submit_btn").removeAttr("disabled");

        });
          $("#value_div_advertising").on('click', '.field_btn', function() {

             $("#value_operand").text($(this).text());
            $("#value_operand").attr('value',$(this).attr('value'))
            $("#submit_btn").removeAttr("disabled");



        });
          $("#value_div_matchtype").on('click', '.field_btn', function() {

             $("#value_operand").text($(this).text());
            $("#value_operand").attr('value',$(this).attr('value'))
            $("#submit_btn").removeAttr("disabled");



        });
        $('.value_text').on('input',function(e){
            $("#value_operand").text($(this).val());
             $("#submit_btn").removeAttr("disabled");
});




        $("#operations_div_string").hide();
        $("#operations_div_number").hide();
        $("#operations_div_label").hide();

        $("#attribute_operation").click(function() {

            if ($(this).val() == 'string') {
                $("#operations_div_string").show();
            } else if ($(this).val() == 'number') {
                $("#operations_div_number").show();
            }
            if ($(this).val() == 'label') {
                $("#operations_div_label").show();
            }


            $("#attributes_div").hide();
             $("#value_div").hide();

        });

        $(".operation_btn").click(function() {
            $("#attribute_operation").text($(this).val());
            $("#attribute_operation").val($(this).val());

        });





        $('#select_scope').change(function() {
            $("#operations_div_string").hide();
            $("#operations_div_number").hide();
            $("#operations_div_label").hide();
            $("#value_div").hide();
            var value = $(this).val();
            var attr_div = $('#attributes_div').html();

            $.ajax({
                type: "POST",
                url: "/condition/",
                data: {
                    'current_scope': value,
                    'csrfmiddlewaretoken': '{{ csrf_token }}'
                },
                success: function(data) {

                    $('#attributes_div').html(data);


                    $("#attributes_div").show();




                }
            });
        });

    });
</script>