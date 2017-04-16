/**
 * Created by neodooth on 4/2/15.
 */

var MAX_IMAGE_PER_PAGE = 30;

$(function () {
    var $item_panel = $('#item-panel');
    var ones = [];
    var all_images = null;
    var is_checked = [];
    var current_page = 0;
    var total_length = 0;
    var selected_number = 0;

    function refreshNumber() {
        $('#number').html('已选择 ' + selected_number);
    }

    function addImagesToImagePanel(images, type, loader) {
        $item_panel.empty();

        var max_page = Math.floor((total_length - 1) / MAX_IMAGE_PER_PAGE);
        if (images.length == 0) {
            $item_panel.append('<h1>没了!');
            return;
        }

        var thisRow = $('<div class="row clearfix"></div>');
        for (var i = 0; i < images.length; ++i) {
            if (i % 6 == 0 && i != 0) {
                $item_panel.append(thisRow);
                thisRow = $('<div class="row clearfix"></div>');
            }

            var $cb = $('<input class="cb" id="checkbox_' + i + '" type="checkbox"/>');
            var image_css = '';
            if (is_checked[i + MAX_IMAGE_PER_PAGE * current_page] == true) {
                $cb.prop('checked', true);
                image_css = 'border: solid 5px cornflowerblue;';
            }

            thisRow.append(
                $('<div class="col-md-2 column pic-of-one" data-id="' + i + '" ></div>')
                    .append('<img id="image_' + i + '" src="' + images[i].url + '?a='+(new Date()).valueOf()+'" class="img-thumbnail" style="' + image_css + '" />')
                    .append($('<div class="caption"></div>').append($cb))
            );

        }
        $item_panel.append(thisRow);

        if (images.length == 0){
                _rects_path = null;
            }
            else{
                _rects_path = images[0].url.split('/')
                _rects_path.pop();
                _rects_path = _rects_path.join('/')+"/_rects";
            };
            // console.log("_rects_path..............",_rects_path);

            $.getJSON(_rects_path,function(rects){
            face_rects = rects;

            for (var i = 0; i < images.length; ++i){
                var image_url = images[i].url;
                var image_rect = face_rects[images[i].id];
                if (image_rect == undefined)
                    continue;
                //console.log("image_url",image_url);
                var image = $("img[src^='" + image_url +"']");
                //console.log("image",image)
                (function(image_rect,image){
                    //console.log("image",image)
                    image.load(function(){
                    var img = new Image();
                    img.src = image[0].src;

                    var width = img.width;
                    var heigth = img.height;

                    if (width >= 163.0){
                    ratio = 163.0/width;
                    //console.log("ratio",ratio,"img.src",img.src);
                   
                    image_rect[0] = ratio * image_rect[0] + 15.0;
                    image_rect[1] = ratio * image_rect[1] + 3.0;
                    image_rect[2] = ratio * image_rect[2];
                    image_rect[3] = ratio * image_rect[3];
                    }

                    image.parent().append('<div class="face-box .img-thumbnail img" style="z-index:2;position:absolute;background-color:rgba(0,0,0,0.2);left:'
                +image_rect[0]+'px;top:'+image_rect[1]+'px;width:'+image_rect[2]+'px;height:'+image_rect[3]+'px;border:1px solid; border-color:red"></div>');

                    })
                })(image_rect,image)
                 
            }

            });

        $('.pic-of-one').click(function () {
            var data_id = $(this).attr('data-id');
            var cb = $('#checkbox_' + data_id);

            var now_status = is_checked[parseInt(data_id) + MAX_IMAGE_PER_PAGE * current_page] != true ? true : false;
            is_checked[parseInt(data_id) + MAX_IMAGE_PER_PAGE * current_page] = now_status;

            cb.prop('checked', now_status);
            console.log(data_id + ' ' + MAX_IMAGE_PER_PAGE * current_page + ' ' + cb.prop('checked'));

            if (cb.prop('checked') == true) {
                ++selected_number;
                $('#image_' + data_id).css('border', 'solid 5px cornflowerblue');
            }
            else{
                --selected_number;
                $('#image_' + data_id).css('border', '');
            }

            refreshNumber();
        });

        if (max_page > 0) {
            var pages = '';
            if (current_page == 0)
                pages += '<li class="disabled"><a class="pagin" id="prev" href="###" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>';
            else pages += '<li><a class="pagin" id="prev" href="#" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>';

            for (var i = 0; i <= max_page; ++i) {
                if (i == current_page)
                    pages += '<li class="active"><a class="pagin" id="' + i + '" href="###">' + (i + 1) + ' <span class="sr-only">(current)</span></a></li>\n';
                else pages += '<li><a class="pagin" id="' + i + '" href="#">' + (i + 1) + ' </a></li>\n';
            }

            if (current_page == max_page)
                pages += '<li class="disabled"><a class="pagin" id="next" href="###" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>';
            else pages += '<li><a class="pagin" id="next" href="#" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>';

            $item_panel.append('\
            <nav> \
              <ul class="pagination"> \
              ' + pages + ' \
              </ul> \
            </nav>');

            $('.pagin').click(function () {
                var action = $(this).attr("id");
                var tmp_page = current_page;
                if (action == 'next') {
                    if (tmp_page < max_page)
                        tmp_page++;
                    else return;
                }
                else if (action == 'prev') {
                    if (tmp_page > 0)
                        tmp_page--;
                    else return;
                }
                else tmp_page = parseInt(action);

                loader(tmp_page * MAX_IMAGE_PER_PAGE, (tmp_page + 1) * MAX_IMAGE_PER_PAGE, function (data) {
                    current_page = tmp_page;
                    addImagesToImagePanel(data, type, loader);
                })
            });
        }
    }

    function loadImages(one) {
        is_checked = [];
        all_images = [];
        if (one == null) {
            addImagesToImagePanel([]);
            return;
        }
        _getImagesOfOne('unannotated', one.id, 0, MAX_IMAGE_PER_PAGE, function (err, len, imgs) {
            if (err != null) {
                alert(err);
                return;
            }
            total_length = len;
            for (var i = 0; i < MAX_IMAGE_PER_PAGE; ++i)
                all_images[i] = imgs[i];

            addImagesToImagePanel(imgs, 'detail', function (from, to, callback) {
                _getImagesOfOne('unannotated', one.id, from, to, function (err, len, imgs) {
                    if (err != null) {
                        alert(err);
                        return;
                    }
                    for (var i = 0; i < MAX_IMAGE_PER_PAGE; ++i)
                        all_images[i + from] = imgs[i];
                    callback(imgs);
                });
            });
        });
        var name = one.chinese_name + ' ' + one.english_name;
        $('#name').html(name);
        refreshNumber();
    }

    function saveImages() {
        var toSave = [];
        for (var i = 0; i < is_checked.length; ++i) {
            if (is_checked[i] == true)
                toSave.push(all_images[i].id);
        }

        var one = ones[0];
        _saveAnnotation(one.id, toSave, function (err, data) {
            if (err != null) {
                alert(err);
                return;
            }

            console.log('delete ' + data + ' images of ' + JSON.stringify(one));

            ones.shift();
            current_page = 0;
            selected_number = 0;
            if (ones.length > 0)
                loadImages(ones[0]);
            else _getList('unannotated', 0, MAX_IMAGE_PER_PAGE, function (len, data) {
                ones = data;
                loadImages(ones[0]);
            });
        });
    }

    function deleteOne() {
        var one = ones.shift();
        _deleteOne('unannotated', one.id, function (data) {
            console.log('deleted ' + JSON.stringify(one));

            current_page = 0;
            selected_number = 0;
            if (ones.length > 0)
                loadImages(ones[0]);
            else _getList('unannotated', 0, MAX_IMAGE_PER_PAGE, function (len, data) {
                ones = data;
                loadImages(ones[0]);
            });
        });
    }

    function select_all() {
        var $cb = $('.cb');
        $cb.prop('checked', true);
        for (var i = 0; i < $cb.length; ++i) {
            is_checked[i + MAX_IMAGE_PER_PAGE * current_page] = true;
            $('#image_' + i).css('border', 'solid 5px cornflowerblue');
        }

        selected_number = 0;
        for (var i = 0; i < is_checked.length; ++i) {
            if (is_checked[i] == true)
                ++selected_number;
        }
        refreshNumber();
    }

    function unselect_all() {
        var $cb = $('.cb');
        $cb.prop('checked', false);
        for (var i = 0; i < $cb.length; ++i) {
            is_checked[i + MAX_IMAGE_PER_PAGE * current_page] = false;
            $('#image_' + i).css('border', '');
        }

        selected_number = 0;
        for (var i = 0; i < is_checked.length; ++i) {
            if (is_checked[i] == true)
                ++selected_number;
        }
        refreshNumber();
    }

    var $save = $('#save');
    var $delete = $('#delete');
    var $unselect_all = $('#unselect-all');
    var $select_all = $('#select-all');

    $save.click(function () {
        if (selected_number == 0) {
            alert('还没选择要保存的图片');
            return;
        }
        saveImages();
    });
    $delete.click(function () {
        deleteOne();
    });
    $unselect_all.click(function () {
        unselect_all();
    });
    $select_all.click(function () {
        select_all();
    });

    function init() {
        _getList('unannotated', 0, MAX_IMAGE_PER_PAGE, function (len, data) {
            ones = data;
            loadImages(ones[0]);
        });
    }

    init();
});