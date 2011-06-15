HEAD_CODE = """
<link rel="stylesheet" href="/ckanext-catalog/css/main.css" 
      type="text/css" media="screen" /> 
"""

BODY_CODE = """
<script type="text/javascript" src="/ckanext-moderatededits/catalog.js"></script>
<script type="text/javascript">
    $('document').ready(function($){
        CKANEXT.CATALOG.init();
    });
</script>
"""
