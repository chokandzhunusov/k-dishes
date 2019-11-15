try {
    document.getElementById("id_file_field").addEventListener('change', f);
} catch {
    console.log('Not file upload dir')
}


function f() {
    numOfFiles = document.getElementById("id_file_field").files.length
    document.getElementById('upload-form-files-num').innerText = numOfFiles + ' файл(а)'
}

function validateFiles() {
    numOfFiles = document.getElementById("id_file_field").files.length
    if (!numOfFiles) {

        let interval = setInterval(function () {
            $("#upload-form-choose-btn").css("background-color", function () {
                this.switch = !this.switch
                return this.switch ? "red" : ""
            });
        }, 500)


        setTimeout(function(){
            clearInterval(interval)
        }, 3000);

    }
}
