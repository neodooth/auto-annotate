/**
 * Created by neodooth on 4/2/15.
 */

/*****
 *
 * @param type 'unannotated', 'annotated', '13000'
 * @param callback callback(data)
 */
function _getList(type, from, to, callback) {
    var $number = null;
    switch (type) {
        case 'undownloaded':
            $number = $('#undownloaded-number');
            break;
        case 'unannotated':
            $number = $('#unannotated-number');
            break;
        case 'annotated':
            $number = $('#annotated-number');
            break;
    }

    $.ajax($SCRIPT_ROOT + '/get_list', {
        data: {type: type, from: from, to: to},
        dataType: 'json',
        error: function (err, status) {
            console.log('get_list ' + type + ' error: ' + JSON.stringify(err) + '. ' + status);
            if (callback)
                callback(null);
        },
        success: function (data) {
            if ($number)
                $number.html(data.length);
            if (callback)
                callback(data.length, data.data);
        }
    });
}

/*****
 *
 * @param type 'unannotated', 'annotated', '13000'
 * @param id this one's name
 * @param callback callback( [ {name: one's name, thumbnail: url of thumbnail}, {}, ...] )
 */
function _getImagesOfOne(type, id, from, to, callback) {
    $.ajax($SCRIPT_ROOT + '/get_images_of_one', {
        data: {type: type, id: id, from: from, to: to},
        dataType: 'json',
        error: function (err, status) {
            console.log('get_images_of_one ' + type + ' ' + id + ' error: ' + JSON.stringify(err) + '. ' + status);
            if (callback)
                callback(null);
        },
        success: function (data) {
            if (data.msg != null) {
                callback(data.msg);
                return;
            }
            callback(null, data.length, data.data);
        }
    });
}

function _saveAnnotation(id, toSaveImageIds, callback) {
    $.ajax($SCRIPT_ROOT + '/save_annotation', {
        type: 'POST',
        data: {id: id, image_ids: JSON.stringify(toSaveImageIds)},
        dataType: 'json',
        error: function (err, status) {
            console.log('save_annotation ' + id + ' error: ' + JSON.stringify(err) + '. ' + status);
            if (callback)
                callback(null);
        },
        success: function (data) {
            callback(data.msg, data);
        }
    });
}

function _deleteOne(type, id, callback) {
    $.ajax($SCRIPT_ROOT + '/delete_one', {
        type: 'POST',
        data: {type: type, id: id},
        dataType: 'json',
        error: function (err, status) {
            console.log('delete_one ' + id + ' error: ' + JSON.stringify(err) + '. ' + status);
            if (callback)
                callback(null);
        },
        success: function (data) {
            if (callback)
                callback(data);
        }
    });
}

function _deleteSomeOfOne(type, id, toDeleteImageIds, callback) {
    $.ajax($SCRIPT_ROOT + '/delete_some_of_one', {
        type: 'POST',
        data: {type: type, id: id, image_ids: JSON.stringify(toDeleteImageIds)},
        dataType: 'json',
        error: function (err, status) {
            console.log('deleteSomeOfOne ' + type + ' ' + id + ' error: ' + JSON.stringify(err) + '. ' + status);
            if (callback)
                callback(null);
        },
        success: function (data) {
            if (callback)
                callback(data);
        }
    });
}

/*****
 *
 * @param namelist: [{
 *                      name: name,
 *                      intro: introduction,
 *                      weibo: weibo address
 *                   },
 *                   {}, ...
 *                  ]
 * @return number of successful submitted names
 */
function submit_namelist(namelist, force_submit, callback) {
    $.ajax($SCRIPT_ROOT + '/submit_namelist', {
        type: 'POST',
        data: {data: JSON.stringify(namelist), force_submit: '' + force_submit},
        dataType: 'json',
        error: function (err, status) {
            console.log('submit_namelist error: ' + JSON.stringify(err) + '. ' + status);
            if (callback)
                callback(null);
        },
        success: function(data) {
            callback(data['msg'], data['has_duplicate'], data['duplicates'])
        }
    });
}

function check_duplicate(id, ch_name, en_name, callback) {
    $.ajax($SCRIPT_ROOT + '/check_duplicate', {
        type: 'POST',
        data: {
            id: id,
            chinese_name: ch_name,
            english_name: en_name
        },
        dataType: 'json',
        error: function (err, status) {
            console.log('submit_namelist error: ' + JSON.stringify(err) + '. ' + status);
            if (callback)
                callback(err);
        },
        success: function(data) {
            callback(data['msg'], data['has_duplicate'], data['duplicates'])
        }
    });
}

function get_info(type, id, callback) {
    $.ajax($SCRIPT_ROOT + '/get_info', {
        data: {type: type, id: id},
        dataType: 'json',
        error: function (err, status) {
            console.log('get_info error' + type + ' ' + id + ' error: ' + JSON.stringify(err) + '. ' + status);
            if (callback)
                callback(null);
        },
        success: function (data) {
            if (callback)
                callback(data);
        }
    });
}

function modify_info(type, id, data, callback) {
    $.ajax($SCRIPT_ROOT + '/modify_info', {
        type: 'POST',
        data: {
            type: type,
            id: id,
            chinese_name: data.chinese_name,
            english_name: data.english_name,
            weibo: data.weibo,
            intro: data.introduction
        },
        error: function (err, status) {
            console.log('modify_info error: ' + JSON.stringify(err) + '. ' + status);
            if (callback)
                callback(err);
        },
        success: function(data) {
            if (data == 'success')
                callback();
            else if (data == 'failed')
                callback('修改失败');
            else callback(data);
        }
    });
}