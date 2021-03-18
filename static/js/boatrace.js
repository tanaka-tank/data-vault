//初期挙動
$(function(){
    var query = window.location.href;
    radio_ele = 0;
    if(getParam('bet_type',query) != null && getParam('bet_type',query) == '3puku'){
        radio_ele = 1;
    }
    if(getParam('bet_type',query) != null && getParam('bet_type',query) == '2tan'){
        radio_ele = 2;
    }
    if(getParam('bet_type',query) != null && getParam('bet_type',query) == '2puku'){
        radio_ele = 3;
    }
    // 要素を取得
    var elements = document.getElementsByName( "tab" ) ;
    // 3つ目の要素を選択状態にする
    elements[radio_ele].checked = true ;

    $( 'input[name="tab"]:radio' ).change( function() {
       var radioval = $(this).val();
       var url = location.href.replace(/\#.*$/, '').replace(/\?.*$/, '');
       if(radioval == '3tan' || radioval == '3puku' || radioval == '2tan' ||radioval == '2puku'){
           document.location.href = url+"?bet_type="+radioval;
       }
    });
});
//更新処理
    function post_data() {
        
        var post_data = {"odds_data_list": []};
        var sutab_list = [];
        $('input[name=odds_check]:checked').each(function() {
            var sub_data = {};
            //var check_v = $(this).val();
            var odds_no = $(this).closest('tr').children("td")[0].getElementsByTagName("input")[1].value;
            //var odds_race_order = $(this).closest('tr').children("td")[1].textContent;
            var odds_race_order = $(this).closest('tr').children("td")[1].getElementsByTagName("input")[0].value;
            var odds = $(this).closest('tr').children("td")[2].getElementsByTagName("input")[0].value;
            //sub_data["odds_check"] = check_v;
            sub_data["odds_no"] = odds_no;
            sub_data["odds_race_order"] = odds_race_order;
            sub_data["odds"] = odds;
            sutab_list.push(JSON.stringify(sub_data));
        });
        if(sutab_list.length === 0){
            return;
        }
        $('.btn').css('pointer-events', 'none');
        //console.log(JSON.stringify(sutab_list));
        post_data["target_odds_list"] = sutab_list;

        var href = window.location.href;
        resultUrl = addUrlParam(href, 'upd', '0', true);
        document.input_form.action = resultUrl;

        // エレメントを作成
        var request = document.createElement('input');
        // データを設定
        request.type = 'hidden';
        request.name = 'post_data_json';
        request.value = JSON.stringify(post_data);
        // 要素を追加
        document.input_form.appendChild(request);
        //document.body.appendChild(form);

        document.input_form.submit();
    }

    //データ取り直し処理
    function update_data() {
        var post_data = {"odds_data_list": []};
        var sutab_list = [];
        $('input[name=odds_check]:checked').each(function() {
            var sub_data = {};
            //var check_v = $(this).val();
            var odds_no = $(this).closest('tr').children("td")[0].getElementsByTagName("input")[1].value;
            //var odds_race_order = $(this).closest('tr').children("td")[1].textContent;
            var odds_race_order = $(this).closest('tr').children("td")[1].getElementsByTagName("input")[0].value;
            var odds = $(this).closest('tr').children("td")[2].getElementsByTagName("input")[0].value;
            //sub_data["odds_check"] = check_v;
            sub_data["odds_no"] = odds_no;
            sub_data["odds_race_order"] = odds_race_order;
            sub_data["odds"] = odds;
            sutab_list.push(JSON.stringify(sub_data));
        });
        if(sutab_list.length === 0){
            return;
        }
        $('.btn').css('pointer-events', 'none');
        
        post_data["target_odds_list"] = sutab_list;
        
        var href = window.location.href;
        resultUrl = addUrlParam(href, 'upd', '1', true);
        document.input_form.action = resultUrl;

        // エレメントを作成
        var request = document.createElement('input');
        // データを設定
        request.type = 'hidden';
        request.name = 'post_data_json';
        request.value = JSON.stringify(post_data);
        // 要素を追加
        document.input_form.appendChild(request);
        //document.body.appendChild(form);

        document.input_form.submit();
    }
    //URLの文字列にクエリ文字列（URLパラメーター）を追加
    //https://shanabrian.com/web/javascript/add-url-query-string.php
var addUrlParam = function(path, key, value, save) {
    if (!path || !key || !value) return '';
 
    var addParam      = key + '=' + value,
        paths         = path.split('/'),
        fullFileName  = paths.pop(),
        fileName      = fullFileName.replace(/[\?#].+$/g, ''),
        dirName       = path.replace(fullFileName, ''),
        hashMatches   = fullFileName.match(/#([^#]+)$/),
        paramMatches  = fullFileName.match(/\?([^\?]+)$/),
        hash          = '',
        param         = '',
        params        = [],
        fullPath      = '',
        hitParamIndex = -1;
 
    if (hashMatches && hashMatches[1]) {
        hash = hashMatches[1];
    }
 
    if (paramMatches && paramMatches[1]) {
        param = paramMatches[1].replace(/#[^#]+$/g, '').replace('&', '&');
    }
 
    fullPath = dirName + fileName;
 
    if (param === '') {
        param = addParam;
    } else if (save) {
        params = param.split('&');
 
        for (var i = 0, len = params.length; i < len; i++) {
            if (params[i].match(new RegExp('^' + key + '='))) {
                hitParamIndex = i;
                break;
            }
        }
 
        if (hitParamIndex > -1) {
            params[hitParamIndex] = addParam;
            param = params.join('&');
        } else {
            param += '&' + addParam;
        }
    } else {
        param += '&' + addParam;
    }
 
    fullPath += '?' + param;
 
    if (hash !== '') fullPath += '#' + hash;
 
    return fullPath;
};
/**
 * Get the URL parameter value
 *
 * @param  name {string} パラメータのキー文字列
 * @return  url {url} 対象のURL文字列（任意）
 */
function getParam(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}