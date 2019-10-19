document.getElementById("id_file_field").addEventListener('change', f);

function f() {
    numOfFiles = document.getElementById("id_file_field").files.length
    document.getElementById('upload-form-files-num').innerText = numOfFiles + ' файл(а)'
}

function validateFiles() {
    numOfFiles = document.getElementById("id_file_field").files.length
    if (!numOfFiles) {
        document.getElementById('upload-form-err-msg').style.display = 'block'

        let interval = setInterval(function () {
            $("#upload-form-err-msg").css("background-color", function () {
                this.switch = !this.switch
                return this.switch ? "red" : ""
            });
        }, 500)


        setTimeout(function(){
            document.getElementById('upload-form-err-msg').style.display = 'none'
            clearInterval(interval)
        }, 3000);

    }
}

