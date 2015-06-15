function readURL(input, tid) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $(tid).attr('src', e.target.result);
        };

        reader.readAsDataURL(input.files[0]);
    }
}
