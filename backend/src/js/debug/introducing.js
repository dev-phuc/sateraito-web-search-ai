/**
 ※本ソースは自動生成されたものです 22/06/2022
 @created: 2022-06-22
 @version: 1.0.0
 @author: Tran Minh Phuc (phuc@vnd.sateraito.co.jp)
 */

(function () {
  /**
   * Change gadget URL
   * @param {string} gadget_id
   * @param {string} hl
   */
  function changeGadgetURL(gadget_id, hl) {
    var gadget_url = SATERAITO_MY_SITE_URL + '/gadget/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + gadget_id + '.xml';
    if (hl != 'ja') {
      gadget_url = gadget_url + '?hl=' + hl;
    }
    $('#gadget_url_' + gadget_id).val(gadget_url);
  }

  /**
   * 新しいGoogleサイト用
   * @param {string} gadget_id
   * @param {string} app_id
   * @param {string} hl
   */
  function changeGadgetURL2(gadget_id, app_id, hl) {
    var gadget_url = '';
    if (gadget_id == 'admin_console' || gadget_id == 'user_console') {
      gadget_url = SATERAITO_MY_SITE_URL + '/gadget/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + app_id + '/'+ gadget_id +'.html?hl=' + hl + '&thd=true';
    }
    $('#gadget_url2_' + gadget_id).val(gadget_url);
  }

  // Value constant
  var gadgetIDList = ['admin_console', 'user_console'];
  var APP_ID_DEFAULT = 'default';

  $(document).ready(function () {
    if (IS_ADMIN == "True") {
      $('#update_impersonate_email').show();
      $('#update_impersonate_email_description').show();
      $('#ImpersonateEmailButtonArea').addClass('updateImpersonateEmailButtonArea');
    }

    $('.select_lang_gadget').change(function (event) {
      var selectedValue = $(this).val();
      var gadgetID = $(this).data('gadget-id');
      changeGadgetURL(gadgetID, selectedValue);
      changeGadgetURL2(gadgetID, APP_ID_DEFAULT, selectedValue);
    });

    for (var i = 0; i < gadgetIDList.length; i++) {
      changeGadgetURL(gadgetIDList[i], SATERAITO_LANG);
      changeGadgetURL2(gadgetIDList[i], APP_ID_DEFAULT, SATERAITO_LANG);
    }

    var btnTmp, strAgent = navigator.userAgent;

    btnTmp = $("#btnExtChrome");
    if (strAgent.indexOf('Chrome') >= 0) {
      $(window).load(function () {
        $("#btnExtChrome").click(function () {
          // 2018.07.18 インラインインストールが廃止されるため、ウェブストアのページを開くように修正。
          // chrome.webstore.install('https://chrome.google.com/webstore/detail/hiceipdnfcepahdbfepcaefppcenhmce');
          window.open('https://chrome.google.com/webstore/detail/hiceipdnfcepahdbfepcaefppcenhmce', "_blank");
        });
      });
    } else {
      btnTmp.attr('disabled', 'disabled');
    }
  });
})();
