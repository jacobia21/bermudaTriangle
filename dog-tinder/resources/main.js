function utoa(str) {
    return window.btoa(unescape(encodeURIComponent(str)));
}

function onSubmitImages(e) {
	if (window.File&&window.FileReader&&window.FileList&&window.Blob) {
    var input = $('#imageInput')[0];
    var outputStr = ''

    if (input.files.length<1) return alert("No files selected.");

    for (var i = 0; i < input.files.length; i++) {
      var file = input.files[i];
    	if (file) {
    		var reader = new FileReader;
    		reader.onload = function(e) {
          /*valueStr = "value = '" + e.target.result + "' ";
          nameStr = "name = 'pic-" + i + "' ";
          outputStr = "<input type='text' " + valueStr + nameStr + " hidden/>";*/
          outputStr += "__break__"
          outputStr += e.target.result;
          alert(outputStr);
    		}
    		reader.readAsDataURL(file);
    	}
    }
    $('#stringOutput').val(function(i,value) {
      return outputStr;
    }).trigger("change");

    $('#submitButton')[0].click();
	}
	else alert("Unsupported browser.");
}

/*function addEvents() {
  $('#submitImgs').on('click',onSubmitImages);
}*/

//$(document).ready(addEvents);
