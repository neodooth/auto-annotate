/**
 * Created by neodooth on 3/25/15.
 */

var MAX_IMAGE_PER_PAGE = 30;

$(function () {
    var $info_panel = $('#info-panel');
    var $item_panel = $('#item-panel');
    var $additional_list = $('#additional-list');
    var unannotated_list = null, annotated_list = null, thirteenthousand_list = null;
    var current_type = null;
    var is_checked = [];
    var current_page = 0, current_id = '';
    var total_length = 0;
    var all_images = [];
    var face_rects = null;
    var _rects_path = null;

    function updateInfoPanel(ch_name, en_name, weibo, intro) {
        $('#info_panel_chinese_name').val(ch_name);
        $('#info_panel_english_name').val(en_name);
        $('#info_panel_weibo').val(weibo);
        $('#info_panel_introduction').val(intro);
    }

    function addImagesToImagePanel(images, type, loader) {
        $item_panel.empty();
        $additional_list.empty();

        var max_page = Math.floor((total_length - 1) / MAX_IMAGE_PER_PAGE);
        if (images.length == 0) {
            $item_panel.append('<h1>没了!');
            return;
        }

        var thisRow = $('<div class="row clearfix"></div>');
        if (type != 'detail') {
            current_type = type;

            for (var i in images) {
                if (i % 6 == 0 && i != 0) {
                    $item_panel.append(thisRow);
                    thisRow = $('<div class="row clearfix"></div>');
                }
                var name = images[i].chinese_name + ' ' + images[i].english_name;
                var img = '';
                if (type == '13000')
                    img = '<img src="' + images[i].thumbnail + '" class="img-thumbnail" data-id="' + i + '">';
                else img = '<a href="###"><img src="' + images[i].thumbnail + '" class="img-thumbnail" data-id="' + i + '"></a>';
                thisRow.append(
                    $('<div class="col-md-2 column"></div>')
                        .append(img)
                        .append('<div class="caption"><p>' + name + '</p></div>')
                );
            }
            $item_panel.append(thisRow);

            if (type != '13000') {
                $('.img-thumbnail').click(function () {
                    showAllImagesOfOne($(this).attr('data-id'));
                });
            }
        }
        else {
            if (current_type == 'unannotated' && current_page == 0)
                alert('选择要删除的图片\n这里选图片不会移到“已标注”');

            $additional_list
                .append('<li id="delete-images"><a href="#">删除选中的</a></li>')
                .append('<li id="delete-one"><a href="#">删除这个人</a></li>')
                .append('<li id="back"><a href="#">返回</a></li>');


            for (var i = 0; i < images.length; ++i) {
                if (i % 6 == 0 && i != 0) {
                    $item_panel.append(thisRow);
                    thisRow = $('<div class="row clearfix"></div>');
                }

                var $cb = $('<input class="cb" id="checkbox_' + i + '" type="checkbox"/>');
                if (is_checked[i + MAX_IMAGE_PER_PAGE * current_page] == true)
                    $cb.prop('checked', true);

                var image_url = images[i].url;
                thisRow.append(
                    $('<div class="col-md-2 column pic-of-one" data-id="' + i + '" ></div>')
                        .append('<img src="' + image_url + '?a='+(new Date()).valueOf()+'" class="img-thumbnail" data-id="' + i + '"></a>')
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

               // console.log("image_url",image_url);
                var image = $("img[src^='" + image_url +"']");
                //console.log("image",image)
                (function(image_rect,image){
                    //console.log("image",image)
                    image.load(function(){
                    var img = new Image();
                    img.src = image[0].src;

                    var width = img.width;
                    var heigth = img.height;
                    //console.log("width",width,"img.src",img.src);

                    if (width >= 163.0){
                    ratio = 163.0/width;
                    //console.log("ratio",ratio,"img.src",img.src);
                   
                    image_rect[0] = ratio * image_rect[0] + 15.0;
                    image_rect[1] = ratio * image_rect[1] + 3.0;
                    image_rect[2] = ratio * image_rect[2];
                    image_rect[3] = ratio * image_rect[3];
                    //console.log(",,,,,,,,,","ratio",ratio,"img.src",img.src,image_rect[0],image_rect[1],image_rect[2],image_rect[3]);
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
                cb.prop('checked', !cb.prop('checked'));
                is_checked[parseInt(data_id) + MAX_IMAGE_PER_PAGE * current_page] = cb.prop('checked');
                console.log(data_id + '+' + MAX_IMAGE_PER_PAGE * current_page + ' ' + cb.prop('checked'));
            });
            $('#delete-images').click(function () {
                var toDelete = [];
                for (var i = 0; i < is_checked.length; ++i) {
                    if (is_checked[i])
                        toDelete.push(all_images[i].id);
                }
                _deleteSomeOfOne(current_type, current_id, toDelete, function (data) {
                    console.log('deleted images of ' + current_id);
                    if (data == 'success') {
                        if (current_type == '13000')
                            alert('已提交删除请求，请鞭笞root去删除');
                        else alert('删除成功');
                        $('#back').click();
                    }
                    else alert('删除失败，稍安勿躁');
                });
            });
            $('#delete-one').click(function () {
                _deleteOne(current_type, current_id, function (data) {
                    console.log('deleted ' + current_id);
                    if (data == 'success') {
                        if (current_type == '13000')
                            alert('已提交删除请求，请鞭笞root去删除');
                        else alert('删除成功');
                        $('#back').click();
                    }
                    else alert('删除失败，稍安勿躁');
                });
            });
            $('#back').click(function () {
                switch (current_type) {
                    case 'unannotated':
                        $show_unannotated.click();
                        break;
                    case 'annotated':
                        $show_annotated.click();
                        break;
                    case '13000':
                        $show_13000.click();
                        break;
                }
            });
        }

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
	
    function showAllImagesOfOne(index) {
        is_checked = [];
        all_images = [];
        current_page = 0;

        var li = [];
        if (current_type == 'unannotated'){
            li = unannotated_list;
        }
        else if (current_type == 'annotated')
            li = annotated_list;
        else if (current_type == '13000')
            li = thirteenthousand_list;
        current_id = li[index].id;
        _getImagesOfOne(current_type, current_id, 0, MAX_IMAGE_PER_PAGE, function (err, len, data) {
            if (err != null) {
                alert(err);
                return;
            }
            total_length = len;
            for (var i = 0; i < len; ++i)
                is_checked[i] = false;
            for (var i = 0; i < MAX_IMAGE_PER_PAGE; ++i)
                all_images[i] = data[i];

            get_info(current_type, current_id, function(data) {
                updateInfoPanel(li[index].chinese_name, li[index].english_name, data.weibo, data.introduction);
                $info_panel.show();
            });

            addImagesToImagePanel(data, 'detail', function (from, to, callback) {
                _getImagesOfOne(current_type, current_id, from, to, function (err, len, data) {
                    if (err != null) {
                        alert(err);
                        return;
                    }
                    for (var i = 0; i < MAX_IMAGE_PER_PAGE; ++i)
                        all_images[i + from] = data[i];
                    callback(data);
                });
            });
        });
    }

    function showSubmitNamesSection() {
        function _addNamelistInput(target, n) {
            var thisDiv = $('<div id="name-list-inputs"></div>');
            for (var i = 0; i < n; ++i) {
                thisDiv.append(
                    '<div id="name-' + i + '" class="row clearfix" style="margin-bottom: 10px"> \
                        <div class="col-md-2 column"> \
                            <div class="input-group"> \
                                <span class="input-group-addon" id="basic-addon1">中文名</span> \
                                <input id="search_person_chinese_name_' + i + '" type="text" class="form-control" aria-describedby="basic-addon1"> \
                            </div> \
                        </div>\
                        <div class="col-md-2 column"> \
                            <div class="input-group"> \
                                <span class="input-group-addon" id="basic-addon1">英文名</span> \
                                <input id="search_person_english_name_' + i + '" type="text" class="form-control" aria-describedby="basic-addon1"> \
                            </div> \
                        </div> \
                        <div class="col-md-2 column"> \
                            <div class="input-group"> \
                                <span class="input-group-addon" id="basic-addon1">搜索关键词</span> \
                                <input id="search_keyword_' + i + '" type="text" class="form-control" aria-describedby="basic-addon1"> \
                            </div> \
                        </div> \
                        <div class="col-md-2 column"> \
                            <div class="input-group"> \
                                <span class="input-group-addon" id="basic-addon1">简介</span> \
                                <input id="search_person_intro_' + i + '" type="text" class="form-control" aria-describedby="basic-addon1"> \
                            </div> \
                        </div> \
                        <div class="col-md-2 column"> \
                            <div class="input-group"> \
                                <span class="input-group-addon" id="basic-addon1">微博地址</span> \
                                <input id="search_person_weibo_' + i + '" type="text" class="form-control" aria-describedby="basic-addon1"> \
                            </div> \
                        </div> \
                        <div class="col-md-2 column"> \
                            <div class="checkbox"> \
                                <label><input type="checkbox" id="dont_detect_face_' + i + '">不检测人脸</label> \
                            </div> \
                        </div> \
                    </div>'
                );
            }
            target.append(thisDiv);

            for (var i = 0; i < n; ++i) {
                (function (index) {
                    $('#search_person_chinese_name_' + index).blur(function () {
                        var ch_name = $('#search_person_chinese_name_' + index).val();
                        var en_name = $('#search_person_english_name_' + index).val();
                        clearDuplicateHighlight(index);
                        if (ch_name.length > 0 || en_name.length > 0) {
                            check_duplicate(index, ch_name, en_name, function (err, has_duplicate, duplicates) {
                                if (has_duplicate == true)
                                    highlightDuplicates(duplicates);
                            });
                        }
                    });
                    $('#search_person_english_name_' + index).blur(function () {
                        var ch_name = $('#search_person_chinese_name_' + index).val();
                        var en_name = $('#search_person_english_name_' + index).val();
                        clearDuplicateHighlight(index);
                        if (ch_name.length > 0 || en_name.length > 0) {
                            check_duplicate(index, ch_name, en_name, function (err, has_duplicate, duplicates) {
                                if (has_duplicate == true)
                                    highlightDuplicates(duplicates);
                            });
                        }
                    });
                })(i);
            }
        }

        function submit_names(force_submit) {
            var $clear_duplicates = $('#clear-duplicates');
            var $force_submit = $('#force-submit-name-list');
            var $submit = $('#submit-name-list');
            $submit.attr('disabled', true);
            $force_submit.attr('disabled', true);

            var inputs = $('#name-list-inputs').children();
            var payload = [];
            for (var i = 0; i < inputs.length; ++i) {
                if (!force_submit) {
                    $('#name-' + i).css('border', '');
                    $('#dup-msg-' + i).remove();
                }

                var data = {
                    id: i,
                    chinese_name: $('#search_person_chinese_name_' + i).val(),
                    english_name: $('#search_person_english_name_' + i).val(),
                    keyword: $('#search_keyword_' + i).val(),
                    intro: $('#search_person_intro_' + i).val(),
                    weibo: $('#search_person_weibo_' + i).val(),
                    dont_detect_face: $('#dont_detect_face_' + i).prop('checked')
                };
                if (data.chinese_name.length > 0 || data.english_name.length > 0)
                    payload.push(data);
            }

            submit_namelist(payload, force_submit, function (err, has_duplicate, duplicates) {
                if (err != null) {
                    alert('提交失败，稍安勿躁：' + err);
                    return;
                }
                if (has_duplicate) {
                    dups = duplicates;
                    highlightDuplicates(duplicates);
                    $('#submit-name-list').attr('disabled', false);
                    $('#force-submit-name-list').attr('disabled', false);
                    $clear_duplicates.fadeIn(200);
                    $force_submit.fadeIn(200);
                    alert('请检查重复项');
                }
                else {
                    alert('提交成功');
                    $show_undownloaded.click();
                }
            });
        }

        function highlightDuplicates(duplicates) {
            for (var i = 0; i < duplicates.length; ++i) {
                var $name = $('#name-' + duplicates[i].id);
                var dups = [];

                for (var j in duplicates[i].existing) {
                    var ch_name = duplicates[i].existing[j].chinese_name;
                    var en_name = duplicates[i].existing[j].english_name;
                    dups.push(duplicates[i].existing[j].username + ' 的' + (ch_name.length > 0 ? ' ' + ch_name : '')
                        + (en_name.length > 0 ? ' ' + en_name : '')
                        + '<img style="max-width: 100px; max-height: 100px;" src="' + duplicates[i].existing[j].thumbnail + '"/>'
                    );
                }

                $name.append('<div id="dup-msg-' + duplicates[i].id + '" class="container"><p>与 ' + dups.join(', ') + ' 重复</p></div>');
                $name.css('border', 'solid 2px red');
            }
        }

        function clearDuplicateHighlight(index) {
            $('[id=dup-msg-' + index + ']').remove();
            $('#name-' + index).css('border', '');
        }

        function clearInput(index) {
            $('#search_person_chinese_name_' + index).val('');
            $('#search_person_english_name_' + index).val('');
            $('#search_keyword_' + index).val('');
            $('#search_person_intro_' + index).val('');
            $('#search_person_weibo_' + index).val('');
            $('#dont_detect_face_' + index).prop('checked', false);
            clearDuplicateHighlight(index);
        }

        var dups = [];

        $item_panel.empty();
        $item_panel.append('<p>实际搜索图片时使用的搜索词是：1.当中文名和英文名都有或只有中文名时，搜索“中文名 关键词”；2.当只有英文名时，搜索“英文名 关键词”</p>');
        $item_panel.append(
            '<div class="row clearfix" style="margin-bottom: 10px"> \
                <div class="col-md-3 column"> \
                    <button id="submit-name-list" type="button" class="btn btn-primary">提交</button> \
                    <button id="clear-duplicates" type="button" class="btn btn-info" style="display: none;">清空重复项</button> \
                    <button id="force-submit-name-list" type="button" class="btn btn-danger" style="display: none;">强制提交</button> \
                </div> \
            </div>'
        );
        _addNamelistInput($item_panel, 10);

        $('#submit-name-list').click(function () {
            submit_names(false);
        });
        $('#clear-duplicates').click(function () {
            for (var i = 0; i < dups.length; ++i) {
                clearInput(dups[i].id);
            }
            $('#clear-duplicates').hide();
            $('#force-submit-name-list').hide();
        });
        $('#force-submit-name-list').click(function () {
            submit_names(true);
        })
    }

    var $show_undownloaded = $('#show-undownloaded');
    var $show_unannotated = $('#show-unannotated');
    var $show_annotated = $('#show-annotated');
    var $show_13000 = $('#show-13000');
    var $show_submit_names = $('#show-submit-names');
    var $info_panel_submit = $('#info_panel_submit_new_info');

    function clearNavbar() {
        $show_undownloaded.removeClass('active');
        $show_unannotated.removeClass('active');
        $show_annotated.removeClass('active');
        $show_13000.removeClass('active');
        $show_submit_names.removeClass('active');
        $additional_list.empty();
        current_page = 0;
        $info_panel.hide();
    }

    $show_undownloaded.click(function () {
        clearNavbar();
        $show_undownloaded.addClass('active');
        _getList('undownloaded', 0, MAX_IMAGE_PER_PAGE, function (len, data) {
            total_length = len;
            addImagesToImagePanel(data, 'undownloaded', function (from, to, callback) {
                _getList('undownloaded', from, to, function (len, data) {
                    callback(data);
                })
            });
        });
    });
    $show_unannotated.click(function () {
        clearNavbar();
        $show_unannotated.addClass('active');
        _getList('unannotated', 0, MAX_IMAGE_PER_PAGE, function (len, data) {
            total_length = len;
            unannotated_list = data;
            addImagesToImagePanel(data, 'unannotated', function (from, to, callback) {
                _getList('unannotated', from, to, function (len, data) {
                    unannotated_list = data;
                    callback(data);
                })
            });
        });
    });
    $show_annotated.click(function () {
        clearNavbar();
        $show_annotated.addClass('active');
        _getList('annotated', 0, MAX_IMAGE_PER_PAGE, function (len, data) {
            total_length = len;
            annotated_list = data;
            addImagesToImagePanel(data, 'annotated', function (from, to, callback) {
                _getList('annotated', from, to, function (len, data) {
                    annotated_list = data;
                    callback(data);
                })
            });
        });
    });
    $show_13000.click(function () {
        clearNavbar();
        $show_13000.addClass('active');
        _getList('13000', 0, MAX_IMAGE_PER_PAGE, function (len, data) {
            total_length = len;
            thirteenthousand_list = data;
            addImagesToImagePanel(data, '13000', function (from, to, callback) {
                _getList('13000', from, to, function (len, data) {
                    thirteenthousand_list = data;
                    callback(data);
                })
            });
        });
    });
    $show_submit_names.click(function () {
        clearNavbar();
        $show_submit_names.addClass('active');
        showSubmitNamesSection();
    });
    $info_panel_submit.click(function () {
        modify_info(
            current_type,
            current_id,
            {
                chinese_name: $('#info_panel_chinese_name').val(),
                english_name: $('#info_panel_english_name').val(),
                weibo: $('#info_panel_weibo').val(),
                introduction: $('#info_panel_introduction').val(),
            },
            function(err) {
                if (err)
                    alert(err);
                else alert('修改成功');
            }
        );
    });

    function init() {
        _getList('undownloaded', 0, MAX_IMAGE_PER_PAGE);
        $show_unannotated.click();
        _getList('annotated', 0, MAX_IMAGE_PER_PAGE);
    }

    init();
});