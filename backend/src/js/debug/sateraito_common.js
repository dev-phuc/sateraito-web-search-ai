/**
 ※本ソースは自動生成されたものです 22/06/2022
 @created: 2022-06-22
 @version: 1.0.0
 @author: Tran Minh Phuc (phuc@vnd.sateraito.co.jp)
 */

(function () {

  Constants = {
    ENABLE_NEW_UI: false,
    SKIN_DEFAULT: 'blue',
    COLOR_SKIN: {
      'facebook': '#0099ff',
      'line': '#07b53b',
      'o365': '#008299',
      'gsite': '#3e50b4',
      'blue': '#2196f3',
      'green': '#4CAF50',
      'yellow': '#F9A825',
      'orange': '#e17e76',
      'red': '#e53935',
      'blue-tiki': '#189eff',
      'blue-sencha': '#025b80',
      'cyan': '#00ACC1',
      'dark-light': '#293039',
      'violet': '#8e44ad',
      'violet-light': '#9f609c',
      'grey': '#7f8c8d',
      'lime': '#1abc9c',
      'teal': '#00897b',
      'pink': '#f783ac',
      'custom': '#ffffff'
    },
    COLORS_FOR_TEMPLATE: [
      '2196F3',
      '4CAF50',
      'F9A825',
      'E17E76',
      'E53935',
      '00ACC1',
      '8E44AD',
      '1ABC9C',
      '000000',
      '993300',
      '333300',
      '003300',
      '003366',
      '000080',
      '333399',
      '333333',
      '800000',
      'FF6600',
      '808000',
      '008000',
      '008080',
      '0000FF',
      '666699',
      '808080',
      'FF0000',
      'FF9900',
      '99CC00',
      '339966',
      '33CCCC',
      '3366FF',
      '800080',
      '969696',
      'FF00FF',
      'FFCC00',
      'FFFF00',
      '00FF00',
      '00FFFF',
      '00CCFF',
      '993366',
      'C0C0C0',
      'FF99CC',
      'FFCC99',
      'FFFF99',
      'CCFFCC',
      'CCFFFF',
      '99CCFF',
      'CC99FF',
      'FFFFFF'
    ],
    REGEX_EMAIL: /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))|([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]{2,})$/,
    REGEX_NUMBER: /^\d+$/,
    REGEX_CATID_URL: /([?|&]caid)=([^&]+)/,
    REGEX_TAG_URL: /([?|&]tl)=([^&]+)/,
    REGEX_DOCCODE_URL: /([?|&]dcd)=([^&]+)/,
    REGEX_CLID_URL: /([?|&]cli)=([^&]+)/,
    REGEX_CLNAME_URL: /([?|&]cln)=([^&]+)/,
    REGEX_FCODE_URL: /([?|&]fc)=([^&]+)/,
    REGEX_FNAME_URL: /([?|&]fn)=([^&]+)/,
    TDATEF_URL: /([?|&]tdf)=([^&]+)/,
    TDATET_URL: /([?|&]tdt)=([^&]+)/,
    KEY_URL: /([?|&]key)=([^&]+)/,
    TAMOUNTF_URL: /([?|&]taf)=([^&]+)/,
    TAMOUNTT_URL: /([?|&]tat)=([^&]+)/,
    FDELETED_URL: /([?|&]fdel)=([^&]+)/,
    REGEX_DOC_ID_OPENING: /([?|&]dio)=([^&]+)/,
    KEY_SPLIT_RAW: '__sateraito__',
    KEY_SPLIT_IN_URL_RAW: ';',
    TRANSACTION_AMOUNT_MAX: 2147483647,
    LOCALES: 'ja-JP',
    FORMAT_DATE: 'Y-m-d',

    TASK_AFTER_CREATED: 'after_created',
    TASK_AFTER_UPDATED: 'after_updated',
    TASK_AFTER_DELETED: 'after_deleted',
    TASK_AFTER_MOVE: 'after_move',
    TASK_AFTER_COPY: 'after_copy',

    SCREEN_ADMIN_CONSOLE: 'admin_console',
    SCREEN_USER_CONSOLE: 'user_console',
    SCREEN_POPUP_FILE_UPLOAD: 'popup_file_upload',

    TASK_SHOW_DETAIL: 'show_detail',
    TASK_SHOW_EDIT: 'show_edit',
    TASK_SHOW_DELETE: 'show_delete',
    TASK_SHOW_FOLDER: 'show_folder',
    TASK_SHOW_FILES_LIST: 'show_files_list',
    TASK_NOT_DO_EVTHING: 'not_do_everything',
    TASK_SEARCH_DOC_BY_CATEGORIES: 'search_doc_by_categories',

    ROOT_FOLDER_NAME: 'Root',
    ROOT_FOLDER_CODE: '__root',

    ACTION_VIEW_FOLDER: 'view_folder',
    ACTION_DELETE_FILE: 'delete_file',
    ACTION_UPLOAD_FILE: 'upload_file',
    ACTION_DOWNLOAD_FILE: 'download_file',

    TYPE_FOLDER: 'folder',
    TYPE_FILE: 'file',
    TYPE_ATTACH_EMAIL: 'attach_email',

    KEY_FILTER_DOC_ALL: 'falldoc',
    KEY_FILTER_DELETED_DOC: 'fdeldoc',
    KEY_FILTER_NOT_DELETED_DOC: 'fnotdeldoc',

    KEY_SELECT_FILE_FROM_LOCAL: 'select_upload_from_local',
    KEY_SELECT_FILE_FROM_GOOGLE_DRIVE: 'select_upload_from_google_drive',

    SEARCH_DOC_SORT_ODER: [
      {value: 'ASCENDING', text: 'TXT_ASC'},
      {value: 'DESCENDING', text: 'TXT_DES'}
    ],
    SEARCH_DOC_SORT_BY: [
      {value: 'author_email', text: 'AUTHOR_EMAIL'},
      {value: 'description', text: 'DESCRIPTION_WORKFLOW_DOC'},
      {value: 'document_code', text: 'DOCUMENT_CODE'},
      {value: 'title', text: 'TITLE_WORKFLOW_DOC'},
      {value: 'transaction_amount', text: 'TRANSACTION_AMOUNT'},
      {value: 'transaction_date', text: 'TRANSACTION_DATE'},
      {value: 'created_date', text: 'CREATED_DATE_AT'},
      {value: 'updated_date', text: 'UPDATED_DATE_AT'},
    ],

    KEY_CODE_CTRL: 17,
    KEY_CODE_C: 67,
    KEY_CODE_V: 86,
    KEY_CODE_X: 88,
    KEY_CODE_DELETE: 46,

    TIME_RECHECK_IMPORT_CLOUD_STORAGE: 5000,

    MAX_SEARCH_RESULT: 100,
    NUM_ATTRIBUTES_MASTER_DATA: 50,

    // Error code
    INVALIDATE_CODE: 'invalidate',
    CANCEL_DO_CODE: 'cancel_do',
    JUST_AWAIT: 'just_await',

    VHTML_STATUS_SYNC_FINISHED: '<p>' + MyLang.getMsg('STATUS_SYNC_FINISHED') + ' <span class="mdi mdi-cloud-check"></span> </p>',
    VHTML_STATUS_SYNC_RUNING: '<p>' + MyLang.getMsg('STATUS_SYNC_RUNING') + ' <span class="mdi mdi-sync ani-circle"></span> </p>',

    USE_CACHE: true,

    CURRENCY_DEFAULT: '円'
  };

  /**
   * SimpleRequest
   *
   * urlを指定してjsonレスポンスを受け取るだけのリクエスト用
   */
  SimpleRequest = {

    /**
     * post
     *
     * 通信エラー等でエラーした場合はコールバックは必ずキックされる
     *
     * @param {object} aParam
     *   callback ... post終了後にキックされる
     *   aEnableRetry ... trueの場合、リトライを最大10回までおこなう
     */
    post: function (aParam) {
      // 必須項目
      var aBaseUrl = aParam['baseUrl'];
      var aMethodUrl = aParam['methodUrl'];
      var aPostData = aParam['postData'];
      if (typeof (aBaseUrl) == 'undefined' || typeof (aMethodUrl) == 'undefined' || typeof (aPostData) == 'undefined') {
        Sateraito.Util.console('** SimpleRequest error aBaseUrl=' + aBaseUrl + ' aMethodUrl=' + aMethodUrl + ' aPostData=' + aPostData);
        return;
      }

      // オプション項目
      var callback = aParam['callback'];
      var enableRetry = aParam['enableRetry'];
      if (typeof (enableRetry) == 'undefined') {
        enableRetry = false;
      }
      var silentMode = aParam['silentMode'];
      if (typeof (silentMode) == 'undefined') {
        silentMode = false;
      }
      var busyMsg = aParam['busyMsg'];
      if (typeof (busyMsg) == 'undefined') {
        busyMsg = '';
      }

      if (IS_OPENID_MODE) {
        // OpenIDモードの場合
        SimpleRequest.postOid(aBaseUrl + '/oid' + aMethodUrl, enableRetry, silentMode, busyMsg, aPostData, callback);
      } else {
        SimpleRequest.postGadgetIO(aBaseUrl + aMethodUrl, enableRetry, silentMode, busyMsg, aPostData, callback);
      }
    },

    /**
     * postGadgetIO
     *
     * ガジェットAPIでpostメソッドを送信
     * 通信エラー等でエラーした場合はコールバックは必ずキックされる
     *
     * @param {string} aUrl
     * @param {boolean} aEnableRetry
     * @param {boolean} aSilentMode
     * @param {string} aBusyMsg
     * @param {object} aPostData
     * @param {function} callback
     * @param {number} aNumRetry
     */
    postGadgetIO: function (aUrl, aEnableRetry, aSilentMode, aBusyMsg, aPostData, callback, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      // 更新していますメッセージを表示
      if (!aSilentMode) {
        if (aBusyMsg == '') {
          SateraitoUI.showLoadingMessage(MyLang.getMsg('UPDATING'));
        } else {
          SateraitoUI.showLoadingMessage(aBusyMsg);
        }
      }

      gadgets.io.makeRequest(aUrl, function (response) {

        // メッセージを消去
        if (!aSilentMode) {
          SateraitoUI.clearMessage();
        }

        if (!response.data) {

          // エラーの場合
          var err = response.errors[0];
          Sateraito.Util.console(err);

          if (aEnableRetry) {
            if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
              // リトライ
              (function () {
                SimpleRequest.postGadgetIO(aUrl, aEnableRetry, aSilentMode, aBusyMsg, aPostData, callback, (aNumRetry + 1));
              }).defer(MyUtil.getWaitMillisec(aNumRetry));
            } else {
              // １０回リトライしたがだめだった
              // エラーメッセージ
              if (response.rc == 401) {
                // ガジェットタイムアウト
                SateraitoUI.showLoadingMessage(MyLang.getMsg('ERROR_TIMEOUT'));
              } else {
                SateraitoUI.showTimerMessage(MyLang.getMsg('ERROR_WHILE_LOADING'), 10);
              }
              // コールバックをキック
              callback({
                status: 'error',
                error_code: 'unknown_error'
              });
            }
          } else {
            // コールバックをキック
            callback({
              status: 'error',
              error_code: 'unknown_error'
            });
          }

          return;
        }

        // コールバックをキック
        var jsondata = response.data;
        if (typeof (callback) == 'function') {
          callback(jsondata);
        }

      }, Sateraito.Util.requestParam(true, aPostData));
    },

    /**
     * postOid
     *
     * @param {string} aUrl
     * @param {boolean} aEnableRetry
     * @param {boolean} aSilentMode
     * @param {string} aBusyMsg
     * @param {object} aPostData
     * @param {function} callback
     * @param {number} aNumRetry
     */
    postOid: function (aUrl, aEnableRetry, aSilentMode, aBusyMsg, aPostData, callback, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      // 更新していますメッセージを表示
      if (!aSilentMode) {
        if (aBusyMsg == '') {
          SateraitoUI.showLoadingMessage(MyLang.getMsg('UPDATING'));
        } else {
          SateraitoUI.showLoadingMessage(aBusyMsg);
        }
      }

      Ext.Ajax.request({
        url: aUrl,
        method: 'POST',
        params: aPostData,
        success: function (response, options) {
          // メッセージを消去
          if (!aSilentMode) {
            SateraitoUI.clearMessage();
          }

          // コールバックをキック
          var jsondata = Ext.decode(response.responseText);
          if (typeof (callback) == 'function') {
            callback(jsondata);
          }
        },
        failure: function (response) {
          // メッセージを消去
          if (!aSilentMode) {
            SateraitoUI.clearMessage();
          }

          // 失敗時
          if (aEnableRetry) {
            if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
              // リトライ
              (function () {
                SimpleRequest.postOid(aUrl, aEnableRetry, aSilentMode, aBusyMsg, aPostData, callback, (aNumRetry + 1));
              }).defer(MyUtil.getWaitMillisec(aNumRetry));
            } else {
              // １０回リトライしたがだめだった
              // エラーメッセージ
              if (response.rc == 401) {
                // ガジェットタイムアウト
                SateraitoUI.showLoadingMessage(MyLang.getMsg('ERROR_TIMEOUT'));
              } else {
                SateraitoUI.showTimerMessage(MyLang.getMsg('ERROR_WHILE_LOADING'), 10);
              }
              // コールバックをキック
              callback({
                status: 'error',
                error_code: 'unknown_error'
              });
            }
          } else {
            // コールバックをキック
            callback({
              status: 'error',
              error_code: 'unknown_error'
            });
          }
        }
      });
    },

    /**
     * get
     *
     * ガジェットIO、OpenID共通
     *
     * @param {string} aParam ... パラメータ指定オブジェクト
     *   baseUrl {string} ... 末尾に「/」は付けない
     *   methodUrl {string} ... 先頭に「/」は必要
     *   callback {function}
     *   silentMode {boolean}
     *   callbackWhenError {boolean} ... 10回リトライして終了した時にコールバックする時にはtrueを指定する
     *   randomWait {boolean} ... 最初のリクエストの前に最大100ミリ秒のランダムなWaitを入れる
     */
    get: function (aParam) {
      // 必須項目
      var aBaseUrl = aParam['baseUrl'];
      var aMethodUrl = aParam['methodUrl'];
      if (typeof (aBaseUrl) == 'undefined' || typeof (aMethodUrl) == 'undefined') {
        Sateraito.Util.console('** SimpleRequest error aBaseUrl=' + aBaseUrl + ' aMethodUrl=' + aMethodUrl);
        return;
      }

      // オプション項目
      var callback = aParam['callback'];
      var aSilentMode = aParam['silentMode'];
      if (typeof (aSilentMode) == 'undefined') {
        aSilentMode = false;
      }
      var aCallbackWhenError = aParam['callbackWhenError'];
      if (typeof (aCallbackWhenError) == 'undefined') {
        aCallbackWhenError = false;
      }
      var randomWait = aParam['randomWait'];
      if (typeof (randomWait) == 'undefined') {
        randomWait = false;
      }

      var goRequest = function () {
        var numRetry = 1;
        if (IS_OPENID_MODE) {
          // OpenIDモードの場合
          SimpleRequest.requestOid(aBaseUrl + '/oid' + aMethodUrl, callback, numRetry, aSilentMode, aCallbackWhenError);
        } else {
          SimpleRequest.requestGadgetIO(aBaseUrl + aMethodUrl, callback, numRetry, aSilentMode, aCallbackWhenError);
        }
      };

      if (randomWait) {
        // 最初のリクエストの前に最大100ミリ秒のランダムなWaitを入れる
        var randomFactor = Math.ceil(Math.random() * 100);
        (function () {
          goRequest();
        }).defer(randomFactor);
      } else {
        goRequest();
      }
    },

    /**
     * requestGadgetIO
     *
     * GaegetIOによりデータを取得する
     *
     * @param {string} aUrl
     * @param {function} callback
     * @param {number} aNumRetry
     * @param {boolean} aSilentMode ... trueにセットすると、読込中メッセージを表示しない。（デフォルトfalse）
     * @param {boolean} aCallbackWhenError ... trueにセットすると、リクエストが失敗された時でもコールバックをキック（デフォルトfalse）
     */
    requestGadgetIO: function (aUrl, callback, aNumRetry, aSilentMode, aCallbackWhenError) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }
      if (typeof (aSilentMode) == 'undefined') {
        aSilentMode = false;
      }
      if (typeof (aCallbackWhenError) == 'undefined') {
        aCallbackWhenError = false;
      }

      if (!aSilentMode) {
        // 読込中メッセージを表示
        SateraitoUI.showLoadingMessage();
      }

      gadgets.io.makeRequest(aUrl, function (response) {

        if (!aSilentMode) {
          // 読込中メッセージを消去
          SateraitoUI.clearMessage();
        }

        if (!response.data) {

          // response error
          var err = response.errors[0];
          Sateraito.Util.console(err);

          SateraitoUI.showTimerMessage(MyLang.getMsg('RELOADING') + ' ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
            // リトライ
            (function () {
              SimpleRequest.requestGadgetIO(aUrl, callback, (aNumRetry + 1), aSilentMode, aCallbackWhenError);
            }).defer(MyUtil.getWaitMillisec(aNumRetry));
          } else {
            // １０回リトライしたがだめだった
            // エラーメッセージ
            if (response.rc == 401) {
              // ガジェットタイムアウト
              SateraitoUI.showLoadingMessage(MyLang.getMsg('ERROR_TIMEOUT'));
            } else {
              SateraitoUI.showTimerMessage(MyLang.getMsg('ERROR_WHILE_LOADING'), 10);
            }

            // 通常コールバックはキックしない
            if (aCallbackWhenError) {
              callback({
                status: 'ng',
                error_code: 'unknown_error'
              });
            }
          }

          return;
        }

        // コールバックをキック
        var jsondata = response.data;
        if (typeof (callback) == 'function') {
          callback(jsondata);
        }

      }, Sateraito.Util.requestParam());
    },

    /**
     * requestOid
     *
     * @param {string} aUrl
     * @param {Function} callback
     * @param {number} aNumRetry
     * @param {boolean} aSilentMode
     * @param {callback} aCallbackWhenError
     */
    requestOid: function (aUrl, callback, aNumRetry, aSilentMode, aCallbackWhenError) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }
      if (typeof (aSilentMode) == 'undefined') {
        aSilentMode = false;
      }
      if (typeof (aCallbackWhenError) == 'undefined') {
        aCallbackWhenError = false;
      }

      if (!aSilentMode) {
        // 読込中メッセージを表示
        SateraitoUI.showLoadingMessage();
      }

      // リクエスト
      Ext.Ajax.request({
        url: aUrl,
        success: function (response, options) {
          if (!aSilentMode) {
            // 読込中メッセージを消去
            SateraitoUI.clearMessage();
          }

          var jsondata = Ext.decode(response.responseText);

          // コールバックをキック
          if (typeof (callback) == 'function') {
            callback(jsondata);
          }
        },
        failure: function () {
          if (!aSilentMode) {
            // 読込中メッセージを消去
            SateraitoUI.clearMessage();
          }
          // 失敗時
          Sateraito.Util.console('retrying ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
            // リトライ
            (function () {
              SimpleRequest.requestOid(aUrl, callback, (aNumRetry + 1), aSilentMode, aCallbackWhenError);
            }).defer(MyUtil.getWaitMillisec(aNumRetry));

          } else {

            // １０回リトライしたがだめだった
            // エラーメッセージ
            if (response.rc == 401) {
              // ガジェットタイムアウト
              SateraitoUI.showLoadingMessage(MyLang.getMsg('ERROR_TIMEOUT'));
            } else {
              SateraitoUI.showTimerMessage(MyLang.getMsg('ERROR_WHILE_LOADING'), 10);
            }

            // 通常コールバックはキックしない
            if (aCallbackWhenError) {
              callback({
                status: 'ng',
                error_code: 'unknown_error'
              });
            }
          }
        }
      });
    }
  };

  /**
   * SateraitoUI
   *
   * 画面系共通API
   */
  SateraitoUI = {

    /**
     * adjustYPosition
     *
     * ガジェットが縦に長い場合に、新規Extウィンドウがガジェットの中央に表示されると都合が悪いため
     * ガジェットの上のあたりに表示されるよう調整する関数
     *
     * @param {object} detailWindow ... 詳細ウィンドウ
     * @param {number} aMaxYPosition ... 最大Yポジション、省略した場合は100
     */
    adjustYPosition: function (detailWindow, aMaxYPosition) {
      var DEFAULT_MAX_Y_POSITION = 200;

      if (typeof (aMaxYPosition) == 'undefined') {
        aMaxYPosition = DEFAULT_MAX_Y_POSITION;
      }

      // 表示の縦位置があまりにも下に行きすぎないよう調整
      var windowPosition = detailWindow.getPosition();
      if (windowPosition[1] > aMaxYPosition) {
        detailWindow.setPagePosition(windowPosition[0], aMaxYPosition);
      }
    },

    /**
     * bindMessageBoxUIListener
     *
     * iframeからのpostMessageを受け取る関数をバインドする
     * 各ガジェット画面の表示時にコールされる
     */
    bindMessageBoxUIListener: function () {
      if (window.addEventListener) {
        // IE以外
        window.addEventListener('message', SateraitoUI.onMessageFromIframe, false);
      } else if (window.attachEvent) {
        // IE8
        window.attachEvent('onmessage', SateraitoUI.onMessageFromIframe);
      }
    },

    /**
     * bindMessageFromParentListener
     *
     * iframeから親フレームのメッセージボックスを表示する際、ボタンの種類が「OKCANCEL」だと
     * この関数をコールして親フレームから「ok」「cancel」どちらを押したかを受信する
     */
    bindMessageFromParentListener: function (callback) {
      SateraitoUI._messageFromParentCallback = callback;

      if (window.addEventListener) {
        // IE以外
        window.addEventListener('message', SateraitoUI.onMessageFromParent, false);
      } else if (window.attachEvent) {
        // IE8
        window.attachEvent('onmessage', SateraitoUI.onMessageFromParent);
      }
    },

    /**
     * MessageBox
     *
     * Ext.Msg.showのラッパー
     *  1)titleを省略してOK、2)縦に長いガジェットでもメッセージがガジェットの中央位置に表示されないよう制御
     *
     * @param {object} aOption
     */
    MessageBox: function (aOption) {
      var icon = typeof (aOption.icon) == 'undefined' ? Ext.MessageBox.INFO : aOption.icon;
      var msg = typeof (aOption.msg) == 'undefined' ? '' : aOption.msg;

      // edited by: tan@vn.sateraito.co.jp - 2019/02/26
      msg = msg.replace(/\n/g, '<br/>');

      var buttons = typeof (aOption.buttons) == 'undefined' ? Ext.Msg.OK : aOption.buttons;
      var fn = typeof (aOption.fn) == 'undefined' ? null : aOption.fn;

      Ext.Msg.show({
        title: MyLang.getMsg('DOCUMENT_MANAGEMENT'),
        icon: icon,
        msg: msg,
        buttons: buttons,
        fn: fn
      });

      // 表示の縦位置があまりにも下に行きすぎないよう調整
      var detailWindow = Ext.Msg;
      var MAX_Y_POSITION = 200;
      var windowPosition = detailWindow.getPosition();
      if (windowPosition[1] > MAX_Y_POSITION) {
        detailWindow.setPagePosition(windowPosition[0], MAX_Y_POSITION);
      }
    },

    _messageFromParentCallback: null,

    /**
     * onMessageFromParent
     *
     * iframeの親からのpostMessageでコールされる関数
     * 親で表示したExtメッセージボックスで「ok」「cancel」ボタンのどちらが押されたか、という情報が
     * postMessageで送信されてくるので、登録されたコールバック関数を「ok」「cancel」どちらかのパラメータでコールバックする
     */
    onMessageFromParent: function (e) {
      if (e.origin === SATERAITO_MY_SITE_URL) {
        if (Sateraito.Util.strStartWith(String(e.data), 'message_box_result:')) {
          var strBody = String(e.data).slice('message_box_result:'.length);
          if (strBody == 'ok') {
            if (typeof (SateraitoUI._messageFromParentCallback) == 'function') {
              // コールバックをキック
              SateraitoUI._messageFromParentCallback('ok');
            }
          } else {
            if (typeof (SateraitoUI._messageFromParentCallback) == 'function') {
              // コールバックをキック
              SateraitoUI._messageFromParentCallback('cancel');
            }
          }
        }

        SateraitoUI.removeMessageFromParentListener();
      }
    },

    /**
     * onMessageFromIframe
     *
     * iframeからのpostMessageによりMessageBoxを表示する
     * ポストされてきたメッセージの例）"message_box:ext-mb-info:OKCANCEL:添付ファイルのショートカットリンクをコピーしました。"
     * 表示ボタンが「OCCANCEL」の場合、押されたボタンに応じてiframeへメッセージをpostする
     *
     * @param {object} e イベント
     */
    onMessageFromIframe: function (e) {
      if (e.origin === SATERAITO_MY_SITE_URL) {
        if (Sateraito.Util.strStartWith(String(e.data), 'message_box:')) {
          var strBody = String(e.data).slice('message_box:'.length);
          // strBody = "ext-mb-info:OKCANCEL:添付ファイルのショートカットリンクをコピーしました。"
          var colonIndex = strBody.indexOf(':');
          var icon = strBody.substr(0, colonIndex);  // icon = "ext-mb-info" (Ext.MessageBox.INFO)
          var strBody2 = strBody.slice(colonIndex + 1);  // strBody2 = "OKCANCEL:添付ファイルのショートカットリンクをコピーしました。"
          var colonIndex2 = strBody2.indexOf(':');
          var buttonKind = strBody2.substr(0, colonIndex2);  // buttonKind = "OKCANCEL"
          var msg = strBody2.slice(colonIndex2 + 1);  // msg = "添付ファイルのショートカットリンクをコピーしました。"

          var buttons = Ext.Msg.OK;
          var fn = null;
          if (buttonKind == 'OKCANCEL') {
            buttons = Ext.Msg.OKCANCEL;
            fn = function (buttonId) {
              if (buttonId == 'ok') {
                e.source.postMessage('message_box_result:ok', SATERAITO_MY_SITE_URL);
              } else {
                e.source.postMessage('message_box_result:cancel', SATERAITO_MY_SITE_URL);
              }
            };
          }

          // ExtJsメッセージボックスの表示
          SateraitoUI.MessageBox({
            icon: icon,
            msg: msg,
            buttons: buttons,
            fn: fn
          });
        }
      }
    },

    /**
     * ParentFrameMessageBox
     *
     * iframeのなかから、親フレームにpostMessageをおこない、親フレームにてExtメッセージボックスを表示する
     * iframeのなかから呼び出す用の関数
     *
     * @param {object} aOption
     */
    ParentFrameMessageBox: function (aOption) {
      var icon = typeof (aOption.icon) == 'undefined' ? Ext.MessageBox.INFO : aOption.icon;
      var msg = typeof (aOption.msg) == 'undefined' ? '' : aOption.msg;
      var buttonKind = 'OK';
      if (typeof (aOption.buttons) != 'undefined' && aOption.buttons != null) {
        if (typeof (aOption.buttons.cancel) != 'undefined' && aOption.buttons.cancel) {
          buttonKind = 'OKCANCEL';
          SateraitoUI.bindMessageFromParentListener(aOption.fn);
        }
      }

      var target = (parent.postMessage ? parent : (parent.document.postMessage ? parent.document : undefined));
      target.postMessage('message_box:' + icon + ':' + buttonKind + ':' + msg, SATERAITO_MY_SITE_URL);
    },

    /**
     * removeMessageFromParentListener
     *
     * iframeのなかから「OKCANCEL」ボタンのメッセージボックスを表示する場合用
     * 用が済んだ親からのメッセージリスナーを削除する
     */
    removeMessageFromParentListener: function () {
      SateraitoUI._messageFromParentCallback = null;

      if (window.removeEventListener) {
        // IE以外
        window.removeEventListener('message', SateraitoUI.onMessageFromParent, false);
      } else if (window.attachEvent) {
        // IE8
        window.detachEvent('onmessage', SateraitoUI.onMessageFromParent);
      }
    },

    /**
     * clearMessage
     *
     * メッセージ表示領域をクリアする
     * ガジェットからもOpenID画面からも共通して呼び出せる
     */
    clearMessage: function () {
      if (IS_OPENID_MODE) {
        // OpenIDモードの場合
        _OidMiniMessage.clearMessage();
      } else {
        // ガジェットモードの場合
        Sateraito.MiniMessage.clearMessage();
      }
    },

    loadingMessageCnt: 0,

    /**
     * showLoadingMessageCnt
     */
    showLoadingMessageCnt: function (aMessageText) {
      if (SateraitoUI.loadingMessageCnt > 0) {
        // すでにメッセージ表示中
        SateraitoUI.loadingMessageCnt++;
      } else {
        // まだメッセージが表示されていなかった
        SateraitoUI.showLoadingMessage(aMessageText);
        SateraitoUI.loadingMessageCnt++;
      }
    },

    /**
     * clearMessageCnt
     */
    clearMessageCnt: function () {
      if (SateraitoUI.loadingMessageCnt > 0) {
        SateraitoUI.loadingMessageCnt--;
      }
      if (SateraitoUI.loadingMessageCnt == 0) {
        SateraitoUI.clearMessage();
      }
    },

    /**
     * showLoadingMessage
     *
     * 読込中メッセージを表示する
     * ガジェットからもOpenID画面からも共通して呼び出せる
     *
     * @param {string} aMessageText 表示するメッセージ
     */
    showLoadingMessage: function (aMessageText) {
      if (typeof (aMessageText) == 'undefined') {
        aMessageText = MyLang.getMsg('LOADING');
      }

      if (IS_OPENID_MODE || IS_TOKEN_MODE || IS_PUBLIC_ANYONE) {
        _OidMiniMessage.showLoadingMessage(aMessageText);
      } else {
        Sateraito.MiniMessage.showLoadingMessage(aMessageText);
      }
    },

    /**
     * showTimerMessage
     *
     * 時間が経つと自動的に消えるメッセージを表示
     * ガジェットからもOpenID画面からも共通して呼び出せる
     *
     * @param {string} aMessageText
     * @param {number} aTime
     */
    showTimerMessage: function (aMessageText, aTime) {
      if (typeof (aTime) == 'undefined') {
        // 指定がない場合、３秒で消す
        aTime = 3;
      }

      if (IS_OPENID_MODE) {
        _OidMiniMessage.showTimerMessage(aMessageText, aTime);
      } else {
        Sateraito.MiniMessage.showTimerMessage(aMessageText, aTime);
      }
    }
  };

  AppsUser = {

    userListLoadingStatus: '0',	// 0=ロード前 1=ロード中 2=ロード完了
    userList: [],
    viewerUserInfo: null,		// ログイン中のユーザーの情報

    /**
     * requestUser
     *
     * ログイン中ユーザーの名前を取得し、ローカルキャッシュに保存する
     *
     * @param {function} callback
     * @param {number} aNumRetry
     */
    requestUser: function (callback, aNumRetry) {
      if (IS_OPENID_MODE) {
        AppsUser._requestUserOid(callback, aNumRetry);
      } else if (IS_TOKEN_MODE) {
        AppsUser._requestUserToken(callback, aNumRetry);
      } else {
        AppsUser._requestUser(callback, aNumRetry);
      }
    },

    /**
     * _requestUser
     *
     * ガジェットIO版
     *
     * @param {function} callback
     * @param {number} aNumRetry
     */
    _requestUser: function (callback, aNumRetry) {
      if (typeof(aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      // 読込中メッセージを表示
      SateraitoUI.showLoadingMessage();

      var url = MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/user/getuser';
      gadgets.io.makeRequest(url, function (response) {

        // ユーザーを取得したときのイベント

        if (!response.data) {

          // response error
          var err = response.errors[0];
          Sateraito.Util.console(err);

          SateraitoUI.showTimerMessage(MyLang.getMsg('RELOADING') + ' ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {

            // 1秒置いてリトライ
            var deferTime = 1000;
            (function () {
              AppsUser._requestUser(callback, (aNumRetry + 1));
            }).defer(deferTime);

          } else {
            // １０回リトライしたがだめだった
            SateraitoUI.showTimerMessage(Sateraito.Lang.getMsg('FAILED_TO_LOAD_USER_INFOMATION'), 10);
          }

          return;
        }

        var jsondata = response.data;

        // ユーザー情報をセット
        AppsUser.viewerUserInfo = jsondata;

        // 読込中メッセージを消去
        SateraitoUI.clearMessage();

        // コールバックをキック
        callback(jsondata);

      }, Sateraito.Util.requestParam());
    },

    /**
     * _requestUserOid
     *
     * OpenID版
     *
     * @param {function} callback
     * @param {number} aNumRetry
     */
    _requestUserOid: function (callback, aNumRetry) {
      // 読込中メッセージを表示
      SateraitoUI.showLoadingMessage();

      if (typeof(aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      // リクエスト
      Ext.Ajax.request({
        url: MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/user/oid/getuser',
        success: function (response, options) {
          var jsondata = Ext.decode(response.responseText);

          // ユーザー一覧をセット
          AppsUser.viewerUserInfo = jsondata;

          // 読込中メッセージを消去
          SateraitoUI.clearMessage();

          // コールバックをキック
          callback(jsondata);
        },
        failure: function () {
          // 失敗時
          Sateraito.Util.console('retrying ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {

            // 1秒置いてリトライ
            var deferTime = 1000;
            (function () {
              AppsUser._requestUserOid(callback, (aNumRetry + 1));
            }).defer(deferTime);

          } else {

            // １０回リトライしたがだめだった
            // 読込中メッセージを消去
            SateraitoUI.clearMessage();
          }
        }
      });
    },

    /**
     * _requestUserToken
     *
     * トークン版
     *
     * @param {function} callback
     * @param {number} aNumRetry
     */
    _requestUserToken: function (callback, aNumRetry) {
      // 読込中メッセージを表示
      SateraitoUI.showLoadingMessage();

      if (typeof(aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      // リクエスト
      Ext.Ajax.request({
        url: MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/user/token/getuser?token=' + USER_TOKEN,
        success: function (response, options) {
          var jsondata = Ext.decode(response.responseText);

          // ユーザー一覧をセット
          AppsUser.viewerUserInfo = jsondata;

          // 読込中メッセージを消去
          SateraitoUI.clearMessage();

          // コールバックをキック
          callback(jsondata);
        },
        failure: function () {
          // 失敗時
          Sateraito.Util.console('retrying ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {

            // 1秒置いてリトライ
            var deferTime = 1000;
            (function () {
              AppsUser._requestUserToken(callback, (aNumRetry + 1));
            }).defer(deferTime);

          } else {

            // １０回リトライしたがだめだった
            // 読込中メッセージを消去
            SateraitoUI.clearMessage();
          }
        }
      });
    },

    /**
     * requestUserList
     *
     * ユーザー一覧をロードしローカルキャッシュにセット
     * 既にロード済みならサーバーにリクエストせず、コールバックをキックして終わり
     *
     * @param {function} callback
     * @param {number} aNumRetry
     */
    requestUserList: function (callback, aNumRetry) {
      // ロード済みの場合、コールバックをキックして終わり
      if (AppsUser.userList.length > 0) {
        if (typeof(callback) == 'function') {
          callback(AppsUser.userList);
        }
        return;
      }

      if (IS_OPENID_MODE) {
        AppsUser._requestUserListOid(callback, aNumRetry);
      } else if (IS_TOKEN_MODE) {
        AppsUser._requestUserListToken(callback, aNumRetry);
      } else {
        AppsUser._requestUserList(callback, aNumRetry);
      }
    },

    /**
     * _requestUserList
     *
     * ユーザー一覧を取得しローカルキャッシュにセット
     * ガジェットIO版
     *
     * @param {Object} callback コールバック関数
     * @param {Number} aNumRetry リトライ回数
     */
    _requestUserList: function (callback, aNumRetry) {
      if (typeof(aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      // ローディングステータスをロード中にセット
      AppsUser.userListLoadingStatus = '1';

      gadgets.io.makeRequest(MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/user/getuserlist', function (response) {

        // ユーザー一覧を取得したときのイベント

        if (!response.data) {

          // response error
          var err = response.errors[0];
          Sateraito.Util.console(err);


          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
            AppsUser._requestUserList(callback, (aNumRetry + 1));
          } else {
            // １０回リトライしたがだめだった
            AppsUser.userListLoadingStatus = '0';
          }

          return;
        }

        AppsUser.userListLoadingStatus = '2';

        var jsondata = response.data;

        // ユーザー一覧をセット
        AppsUser.userList = jsondata;

        // コールバックをキック
        if (typeof(callback) == 'function') {
          callback(jsondata);
        }

      }, Sateraito.Util.requestParam());
    },

    /**
     * _requestUserListOid
     *
     * @param {function} callback
     * @param {number} aNumRetry
     */
    _requestUserListOid: function (callback, aNumRetry) {
      if (typeof(aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      // ローディングステータスをロード中にセット
      AppsUser.userListLoadingStatus = '1';

      // リクエスト
      Ext.Ajax.request({
        url: MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/user/oid/getuserlist',
        success: function (response, options) {
          // ローディングステータスを完了にセット
          AppsUser.userListLoadingStatus = '2';

          var jsondata = Ext.decode(response.responseText);

          // ユーザー一覧をセット
          AppsUser.userList = jsondata;

          // コールバックをキック
          if (typeof(callback) == 'function') {
            callback(jsondata);
          }
        },
        failure: function () {
          // 失敗時
          Sateraito.Util.console('retrying ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {

            // リトライ
            AppsUser._requestUserListOid(callback, (aNumRetry + 1));

          } else {

            // １０回リトライしたがだめだった
          }
        }
      });
    },

    /**
     * _requestUserListToken
     *
     * @param {function} callback
     * @param {number} aNumRetry
     */
    _requestUserListToken: function (callback, aNumRetry) {
      if (typeof(aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      // ローディングステータスをロード中にセット
      AppsUser.userListLoadingStatus = '1';

      // リクエスト
      Ext.Ajax.request({
        url: MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/user/token/getuserlist?token=' + USER_TOKEN,
        success: function (response, options) {
          // ローディングステータスを完了にセット
          AppsUser.userListLoadingStatus = '2';

          var jsondata = Ext.decode(response.responseText);

          // ユーザー一覧をセット
          AppsUser.userList = jsondata;

          // コールバックをキック
          if (typeof(callback) == 'function') {
            callback(jsondata);
          }
        },
        failure: function () {
          // 失敗時
          Sateraito.Util.console('retrying ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {

            // リトライ
            AppsUser._requestUserListToken(callback, (aNumRetry + 1));

          } else {

            // １０回リトライしたがだめだった
          }
        }
      });
    },

    /**
     * requestToken
     *
     * ユーザートークンの取得
     *
     * @param {function} callback
     * @param {boolean} aRenew
     */
    requestToken: function (callback, aRenew) {
      if (typeof(aRenew) == 'undefined') {
        aRenew = false;
      }
      if (typeof(PUBLIC_ANYONE) === 'undefined')
        PUBLIC_ANYONE = false

      if (PUBLIC_ANYONE) {
        callback({
          token: ''
        });
      } else if (IS_OPENID_MODE) {
        AppsUser._requestTokenOid(callback, aRenew);
      } else if (IS_TOKEN_MODE) {
        callback({
          token: USER_TOKEN
        });
      } else {
        AppsUser._requestToken(callback, aRenew);
      }
    },

    /**
     * _requestToken
     *
     * ユーザートークンの取得（ガジェットIO版）
     *
     * @param {Function} callback
     * @param {number} aNumRetry
     */
    _requestToken: function (callback, aRenew, aNumRetry) {
      if (typeof(aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }
      var db_name = $("#mainPanelWrapper").attr("init_db");
      if (db_name != "" && db_name != null) {
        var url = MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + db_name + '/gettoken' + (aRenew ? '?renew=1' : '');
      } else {
        var url = MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/gettoken' + (aRenew ? '?renew=1' : '');
      }

      gadgets.io.makeRequest(url, function (response) {

        if (!response.data) {

          // response error
          var err = response.errors[0];
          Sateraito.Util.console(err);

          SateraitoUI.showTimerMessage(MyLang.getMsg('RELOADING') + ' ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
            AppsUser._requestToken(callback, aRenew, (aNumRetry + 1));
          } else {
            // １０回リトライしたがだめだった
            SateraitoUI.showTimerMessage(Sateraito.Lang.getMsg('FAILED_TO_LOAD_SETTINGS'), 10);
          }

          return;
        }

        var jsondata = response.data;

        // コールバックをキック
        callback(jsondata);

      }, Sateraito.Util.requestParam());
    },

    /**
     * _requestTokenOid
     *
     * ユーザートークンの取得（OpenID版）
     *
     * @param {function} callback
     * @param {number} aNumRetry
     */
    _requestTokenOid: function (callback, aRenew, aNumRetry) {
      // 読込中メッセージを表示
      SateraitoUI.showLoadingMessage();

      if (typeof(aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }
      var db_name = $("#mainPanelWrapper").attr("init_db");
      if (db_name != "" && db_name != null) {
        var my_url = MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + db_name + '/oid/gettoken' + (aRenew ? '?renew=1' : '');
      } else {
        var my_url = MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/oid/gettoken' + (aRenew ? '?renew=1' : '');
      }

      // リクエスト
      Ext.Ajax.request({
//        url: MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/oid/gettoken' + (aRenew ? '?renew=1' : ''),
        url: my_url,
        success: function (response, options) {
          var jsondata = Ext.decode(response.responseText);

          // 読込中メッセージを消去
          SateraitoUI.clearMessage();

          // コールバックをキック
          callback(jsondata);
        },
        failure: function () {
          // 失敗時
          Sateraito.Util.console('retrying ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {

            // リトライ
            AppsUser._requestTokenOid(callback, aRenew, (aNumRetry + 1));

          } else {

            // １０回リトライしたがだめだった
            // 読込中メッセージを消去
            SateraitoUI.clearMessage();
          }
        }
      });
    },

        /**
		 * requestOneTimeToken
		 *
		 * ワンタイムトークンの取得
		 *
		 * @param {boolean} aForPreview
		 * @param {Function} callback
		 */
		requestOneTimeToken: function(app_id, aForPreview, callback, aNumRetry)
		{

			// 添付ファイル領域とかだと IS_OPENID_MODE = False なのに iframe（=gadgetsじゃない）だったりするので、微妙だけど「gadgets」で判断してみる...
			//if (IS_OPENID_MODE) {
      if (IS_OPENID_MODE) {
        AppsUser._requestOneTimeOid(app_id, aForPreview, callback);
      }
      else if(IS_TOKEN_MODE){
        AppsUser._requestOneTimeTokenOid(app_id, aForPreview, callback);
      }
      else {
        AppsUser._requestOneTimeToken(app_id, aForPreview, callback);
      }
		},

		/**
		 * _requestOneTimeToken
		 *
		 * ワンタイムトークンの取得（ガジェットIO版）
		 *
		 * @param {boolean} aForPreview
		 * @param {Function} callback
		 * @param {number} aNumRetry
		 */
		_requestOneTimeToken: function(app_id, aForPreview, callback, aNumRetry)
		{
      if (typeof(aForPreview) == 'undefined') {
				aForPreview = false;
			}
			if (typeof(aNumRetry) == 'undefined') {
				aNumRetry = 1;
			}

			gadgets.io.makeRequest(SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + app_id + '/getonetimetoken?hl=' + SATERAITO_LANG + '&for_preview=' + (aForPreview ? '1' : '0'), function(response) {

				if (!response.data) {

					// response error
					var err = response.errors[0];
					Sateraito.Util.console(err);

					//SateraitoUI.showTimerMessage(MyLang.getMsg('RELOADING') + ' ' + aNumRetry);

					if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
						// リトライ
						AppsUser._requestOneTimeToken(app_id, aForPreview, callback, (aNumRetry + 1));
					//} else {
						// １０回リトライしたがだめだった
						//if (response.rc == 401) {
						//	// ガジェットタイムアウト
						//	SateraitoUI.showLoadingMessage(MyLang.getMsg('ERROR_TIMEOUT'));
						//} else {
						//	SateraitoUI.showTimerMessage(MyLang.getMsg('FAILED_TO_LOAD_SETTINGS'), 10);
						//}
					}

					return;
				}

				var jsondata = response.data;

				// コールバックをキック
				callback(jsondata);

			}, Sateraito.Util.requestParam());
		},

		/**
		 * _requestOneTimeTokenOid
		 *
		 * ワンタイムトークンの取得（OpenID版）
		 *
		 * @param {boolean} aForPreview
		 * @param {Function} callback
		 * @param {number} aNumRetry
		 */
		_requestOneTimeOid: function(app_id, aForPreview, callback, aNumRetry)
		{
			// 読込中メッセージを表示
			SateraitoUI.showLoadingMessage();
			if (typeof(aNumRetry) == 'undefined') {
				aNumRetry = 1;
			}
			if (typeof(aForPreview) == 'undefined') {
				aForPreview = false;
			}

			// リクエスト
			Ext.Ajax.request({
				url: SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + app_id + '/oid/getonetimetoken?hl=' + SATERAITO_LANG + '&for_preview=' + (aForPreview ? '1' : '0'),
				success: function(response, options)
				{
					var jsondata = Ext.decode(response.responseText);

					// 読込中メッセージを消去
					SateraitoUI.clearMessage();

					// コールバックをキック
					callback(jsondata);
				},
				failure: function()
				{
					// 失敗時
					Sateraito.Util.console('retrying ' + aNumRetry);

					if (aNumRetry < Sateraito.EventController.MAX_RETRY) {

						// リトライ
						AppsUser._requestOneTimeOid(app_id, aForPreview, callback, (aNumRetry + 1));

					} else {

						// １０回リトライしたがだめだった

						// 読込中メッセージを消去
						SateraitoUI.clearMessage();
					}
				}
			});
		},
		/**
		 * _requestOneTimeTokenOid
		 *
		 * ワンタイムトークンの取得（OpenID版）
		 *
		 * @param {boolean} aForPreview
		 * @param {Function} callback
		 * @param {number} aNumRetry
		 */
		_requestOneTimeTokenOid: function(app_id, aForPreview, callback, aNumRetry)
		{
			// 読込中メッセージを表示
			SateraitoUI.showLoadingMessage();
			if (typeof(aNumRetry) == 'undefined') {
				aNumRetry = 1;
			}
			if (typeof(aForPreview) == 'undefined') {
				aForPreview = false;
			}

			// リクエスト
			Ext.Ajax.request({
				url: SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + app_id + '/token/getonetimetoken?token='+ USER_TOKEN + '&hl=' + SATERAITO_LANG + '&for_preview=' + (aForPreview ? '1' : '0'),
				success: function(response, options)
				{
					var jsondata = Ext.decode(response.responseText);

					// 読込中メッセージを消去
					SateraitoUI.clearMessage();

					// コールバックをキック
					callback(jsondata);
				},
				failure: function()
				{
					// 失敗時
					Sateraito.Util.console('retrying ' + aNumRetry);

					if (aNumRetry < Sateraito.EventController.MAX_RETRY) {

						// リトライ
						AppsUser._requestOneTimeTokenOid(app_id, aForPreview, callback, (aNumRetry + 1));

					} else {

						// １０回リトライしたがだめだった

						// 読込中メッセージを消去
						SateraitoUI.clearMessage();
					}
				}
			});
		},

    /**
     * getUser
     *
     * @param {String} aUserEmail
     * @return {Object}
     */
    getUser: function (aUserEmail) {
      var ret = null;
      $.each(AppsUser.userList, function (i, user) {
        if (user.user_email == aUserEmail) {
          ret = user;
          // ここの「return false」は、$.eachを抜けるためのもの
          return false;
        }
      });
      return ret;
    },

    /**
     * getUserName
     *
     * メールアドレスよりユーザー名を返す
     *
     * @param {String} aUserEmail
     * @return {String} ユーザー名
     */
    getUserName: function (aUserEmail) {
      var user = AppsUser.getUser(aUserEmail);
      if (user == null) {
        return aUserEmail;
      }
      return user.family_name + user.given_name;
    }
  };

  /**
   * GoogleAppsグループを管理するモジュール
   */
  AppsGroup = {

    groupList: [],
    groupListLoadingStatus: '0',

    /**
     * getGroupName
     *
     * グループメールアドレスからグループ名を返す
     *
     * @param {string} aEmail
     * @return {string}
     */
    getGroupName: function (aEmail) {
      var retName = aEmail;
      Ext.each(AppsGroup.groupList, function () {
        var groupId = '' + this.group_id;
        if (groupId == aEmail) {
          retName = '' + this.group_name;
        }
      });
      return retName;
    },

    /**
     * requestAllGroupOfMember
     *
     * 自分の所属するグループ一覧をサーバー側メモリーにロードするのをリクエスト
     *
     * @param {function} callback
     * @param {number} aNumRetry
     */
    requestAllGroupOfMember: function (callback, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      var baseUrl = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/group';
      var methodUrl = '/loadallgroupofuser';

      SimpleRequest.get({
        baseUrl: baseUrl,
        methodUrl: methodUrl,
        enableRetry: true,
        callback: function (jsondata) {
          if (typeof (callback) == 'function') {
            callback();
          }
        }
      });

      /*var url = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/group/loadallgroupofuser';
      gadgets.io.makeRequest(url, function(response){

        if (!response.data) {

          // response error
          var err = response.errors[0];
          Sateraito.Util.console(err);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
            // リトライ
            AppsGroup.requestAllGroupOfMember(callback, (aNumRetry + 1));
          } else {
            // エラーメッセージ
            if(response.rc == 401){
              SateraitoUI.showLoadingMessage(MyLang.getMsg('ERROR_TIMEOUT'));
            } else {
              SateraitoUI.showTimerMessage(MyLang.getMsg('ERROR_WHILE_LOADING'), 10);
            }
          }

          return;
        }

        var jsondata = response.data;

        if (typeof(callback) == 'function') {
          callback();
        }

      }, Sateraito.Util.requestParam());*/
    },

    /**
     * requestGroupList
     *
     * ユーザー一覧をロードしローカルキャッシュにセット
     * 既にロード済みならサーバーにリクエストせず、コールバックをキックして終わり
     *
     * @param {function} callback
     * @param {number} aNumRetry
     */
    requestGroupList: function (callback, aNumRetry) {
      if (AppsGroup.groupList.length > 0) {
        if (typeof (callback) == 'function') {
          callback(AppsGroup.groupList);
        }
        return;
      }

      if (IS_OPENID_MODE) {
        AppsGroup._requestGroupListOid(callback, aNumRetry);
      } else {
        AppsGroup._requestGroupList(callback, aNumRetry);
      }
    },

    /**
     * _requestGroupList
     *
     * ユーザー一覧を取得しローカルキャッシュにセット
     * ガジェットIO版
     *
     * @param {Object} callback コールバック関数
     * @param {Number} aNumRetry リトライ回数
     */
    _requestGroupList: function (callback, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      // ローディングステータスをロード中にセット
      AppsGroup.groupListLoadingStatus = '1';

      var url = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/group/getgrouplist';
      gadgets.io.makeRequest(url, function (response) {

        // ユーザー一覧を取得したときのイベント

        if (!response.data) {

          // response error
          var err = response.errors[0];
          Sateraito.Util.console(err);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {

            // aNumRetry秒後にリトライ
            (function () {
              AppsGroup._requestGroupList(callback, (aNumRetry + 1));
            }).defer(1000 * aNumRetry);

          } else {
            // １０回リトライしたがだめだった
            AppsGroup.groupListLoadingStatus = '0';
          }

          return;
        }

        AppsGroup.groupListLoadingStatus = '2';

        var jsondata = response.data;

        // グループ一覧をセット
        AppsGroup.groupList = jsondata;

        // コールバックをキック
        if (typeof (callback) == 'function') {
          callback(jsondata);
        }

      }, Sateraito.Util.requestParam());
    },

    /**
     * _requestGroupListOid
     *
     * @param {function} callback
     * @param {number} aNumRetry
     */
    _requestGroupListOid: function (callback, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      // ローディングステータスをロード中にセット
      AppsGroup.groupListLoadingStatus = '1';

      // リクエスト
      Ext.Ajax.request({
        url: SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/group/oid/getgrouplist',
        success: function (response, options) {
          // ローディングステータスを完了にセット
          AppsGroup.groupListLoadingStatus = '2';

          var jsondata = Ext.decode(response.responseText);

          // ユーザー一覧をセット
          AppsGroup.groupList = jsondata;

          // コールバックをキック
          if (typeof (callback) == 'function') {
            callback(jsondata);
          }
        },
        failure: function () {
          // 失敗時
          Sateraito.Util.console('retrying ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {

            // aNumRetry秒後にリトライ
            (function () {
              AppsGroup._requestGroupListOid(callback, (aNumRetry + 1));
            }).defer(1000 * aNumRetry);

          } else {

            // １０回リトライしたがだめだった
          }
        }
      });
    }
  };

  _OidMiniMessage = {

    /**
     * clearMsg
     */
    clearMessage: function () {
      $('#mini_message').html('');
    },

    /**
     * showLoadingMessage
     *
     * 読込中メッセージを表示する
     */
    showLoadingMessage: function (aMessageText) {
      if (typeof (aMessageText) == 'undefined') {
        aMessageText = MyLang.getMsg('LOADING');

      }

      // ミニメッセージを消去
      $('#mini_message').html('');
      $('#mini_message').css('width', '250px');

      // メッセージの位置を再配置
      var bodyWidth = $('#mini_message').parent().width();
      var messageAreaWidth = $('#mini_message').width();
      $('#mini_message').css('left', '' + ((bodyWidth / 2) - (messageAreaWidth / 2)) + 'px');

      // ミニメッセージを表示
      $('#mini_message').text(aMessageText)
        .css('width', '250px')
        .css('font-size', '1.4em')
        .css('font-weight', 'bold')
        .css('background-color', 'lemonchiffon')
        .css('text-align', 'center');
    },

    /**
     * showTimerMessage
     *
     * @param {string} aMessage
     * @param {number} aWait
     */
    showTimerMessage: function (aMessage, aWait) {
      // デフォルト３秒で自動的に消える
      if (typeof (aWait) == 'undefined') {
        aWait = 3;
      }

      // ミニメッセージを消去
      $('#mini_message').html('');
      $('#mini_message').css('width', '350px');

      // ミニメッセージの位置を再配置
      var bodyWidth = $('#mini_message').parent().width();
      var messageAreaWidth = $('#mini_message').width();
      $('#mini_message').css('left', '' + ((bodyWidth / 2) - (messageAreaWidth / 2)) + 'px');

      // ミニメッセージを表示
      $('#mini_message').text(aMessage)
        .css('font-size', '1.4em')
        .css('width', '350px')
        .css('font-weight', 'bold')
        .css('background-color', 'lemonchiffon')
        .css('text-align', 'center');

      (function () {
        // ミニメッセージを消去
        $('#mini_message').html('').css('width', '0px');
      }).defer(aWait * 1000);
    },

    /**
     * showErrMiniMessage
     *
     * @param {String} aMessage
     */
    showErrMiniMessage: function (aMessage) {
      // ミニメッセージを消去
      $('#mini_message').html('');
      $('#mini_message').css('width', '400px');

      // ミニメッセージの位置を再配置
      var bodyWidth = $('#mini_message').parent().width();
      var messageAreaWidth = $('#mini_message').width();
      $('#mini_message').css('left', '' + ((bodyWidth / 2) - (messageAreaWidth / 2)) + 'px');

      // ミニメッセージを表示
      $('#mini_message').text(aMessage)
        .css('font-size', '1.2em')
        .css('width', '400px')
        .css('font-weight', 'bold')
        .css('background-color', 'pink')
        .css('text-align', 'center');

      (function () {
        // ミニメッセージを消去
        $('#mini_message').html('').css('width', '0px');
      }).defer(3000);
    }
  };

  /**
   * その他便利機能
   */
  MyUtil = {

    /**
     * getMode
     */
    getMode: function () {
      if (typeof (MODE) != 'undefined' && MODE != null) {
        if (MODE == 'sharepoint' || MODE == 'ssite' || MODE == 'ssogadget') {
          return MODE;
          // GoogleSiteの場合は空
        } else {
          return '';
        }
      } else {
        return IS_SHAREPOINT_MODE ? 'sharepoint' : '';
      }
    },

    /**
     * getUrlParams
     *
     * @return {object} urlに指定されたGETパラメータ
     */
    getUrlParams: function () {
      var
        vars = [],
        hash,
        iPos,
        strUrl,
        hashes;

      strUrl = window.location.href;
      iPos = strUrl.indexOf('?');

      if (iPos >= 0) {
        hashes = strUrl.slice(iPos + 1).split('&');

        for (var i = 0; i < hashes.length; i++) {
          hash = hashes[i].split('=');
          vars.push(hash[0]);
          vars[hash[0]] = decodeURIComponent(hash[1]);
        }
      }

      return vars;
    },

    /**
     * getViewEmailDomainPart
     *
     * @return {string} ログインユーザーのドメイン
     */
    getViewEmailDomainPart: function () {
      var viewerEmailSplited = ('' + LoginMgr.getViewerEmail()).split('@');
      return viewerEmailSplited[1];
    },

    /**
     * isMultiDomainSetting
     *
     * @return {boolean} マルチドメイン設定かどうか
     */
    isMultiDomainSetting: function () {
      return LoginMgr.multiDomainSetting;
    },

    /**
     * isSubdomainUser
     *
     * @return {boolean} ユーザーがサブドメインのユーザーかどうか
     */
    isSubdomainUser: function () {
      var userDomain = MyUtil.getViewEmailDomainPart();
      return SATERAITO_GOOGLE_APPS_DOMAIN != userDomain
    },

    /**
     * isValidBbsId
     *
     * @param {string} aAppId
     */
    isValidBbsId: function (aAppId) {
      // 開始文字がアルファベットで、
      // 文字種がアルファベット及び数字、アンダーバー、ハイフンかどうかチェック
      var re = new RegExp('^[a-zA-Z][a-zA-Z0-9_\-]+$');
      if (!re.test(aAppId)) {
        return false;
      }
      // アンダーバー５つが含まれていないかどうかチェック
      var splited = aAppId.split('_____');

      if (splited.length > 1) {
        return false;
      }

      return true;
    },

    /**
     * isValidAppId
     *
     * @param {string} aAppId
     */
    isValidAppId: function (aAppId) {
      // 開始文字がアルファベットで、
      // 文字種がアルファベット及び数字、アンダーバー、ハイフンかどうかチェック
      var re = new RegExp('^[a-zA-Z][a-zA-Z0-9_\-]+$');
      if (!re.test(aAppId)) {
        return false;
      }
      // アンダーバー５つが含まれていないかどうかチェック
      var splited = aAppId.split('_____');
      if (splited.length > 1) {
        return false;
      }

      return true;
    },

    /**
     * getWaitMillisec
     *
     * exponential backoffを実装した待ち時間を返す（ミリ秒）
     *
     * @param {number} aNumRetry ... リトライ回数、最初の数は1とする
     * @return {number} 待ち時間（ミリ秒）
     */
    getWaitMillisec: function (aNumRetry) {
      // 0～1秒のランダム
      var randomFactor = Math.ceil(Math.random() * 1000);

      // 1, 2, 4, 8, 16, 32, 60, 60, 60, 60...
      var exponentialFactor = Math.pow(2, (aNumRetry - 1)) * 1000;
      if (exponentialFactor > 60 * 1000) {
        exponentialFactor = 60 * 1000;
      }
    },

    copyToClipboard: function (aFormat, copyText) {
      var eleArea;
      eleArea = document.getElementById('idForCopyElement');
      if (!eleArea) {
        if (aFormat === 'text/html') {
          eleArea = document.createElement('div');
        } else {
          eleArea = document.createElement('textarea');
        }
        eleArea.id = 'idForCopyElement';
        eleArea.readOnly = true;
        eleArea.style = 'position:absolute; top:0; left:-10; width:1px; height:1px; border:none;';
        document.body.appendChild(eleArea);
      }
      if (eleArea) {
        // 値セット
        if (aFormat === 'text/html') {
          $('#idForCopyElement').append(copyText);
        } else {
          eleArea.value = copyText;
        }
        // 範囲選択
        if (aFormat == 'text/html') {
          var range = document.createRange();
          range.selectNodeContents(eleArea);
          var selection = window.getSelection();
          selection.removeAllRanges();
          selection.addRange(range);
        } else {
          eleArea.select();
        }
        // コピー
        document.execCommand('copy');
        // コピー用エレメントの削除
        //selection.removeAllRanges();
        $('#idForCopyElement').remove();
      }
    },

    /**
     * getUrlQueries
     *
     * @return {object}
     */
    getUrlQueries: function () {
      var queryStr = window.location.search.slice(1);  // 文頭?を除外
      queries = {};

      // クエリがない場合は空のオブジェクトを返す
      if (!queryStr) {
        return queries;
      }

      // クエリ文字列を & で分割して処理
      queryStr.split('&').forEach(function (queryStr) {
        // = で分割してkey,valueをオブジェクトに格納
        var queryArr = queryStr.split('=');
        queries[queryArr[0]] = queryArr[1];
      });

      return queries;
    },

    /**
     * setClipboardValue
     *
     * ブラウザのClipboard APIを使ってクリップボードに値をセットする
     *
     * @param {string} aFormat ... 'text/plain' や 'text/html'
     * @param {string} aValue ... クリップボードにセットする値
     * @param {callback} callback
     */
    setClipboardValue: function (aFormat, aValue, callback) {
      var ua = window.navigator.userAgent.toLowerCase();
      // Edge対応 2016.11.30
      if (ua.match('edge')) {

        //aFormat = 'text/plain';
        var eleArea;
        eleArea = document.getElementById('idForCopyElement');
        if (!eleArea) {
          if (aFormat == 'text/html') {
            eleArea = document.createElement('div');
          } else {
            eleArea = document.createElement('textarea');
          }
          eleArea.id = 'idForCopyElement';
          eleArea.readOnly = true;
          eleArea.style = 'position:absolute; top:0; left:-10; width:1px; height:1px; border:none;';
          //eleArea.style.display = 'none';
          document.body.appendChild(eleArea);
        }
        if (eleArea) {
          // 値セット
          if (aFormat == 'text/html') {
            $('#idForCopyElement').append(aValue);
          } else {
            eleArea.value = aValue;
          }
          // 範囲選択
          if (aFormat == 'text/html') {
            var range = document.createRange();
            range.selectNodeContents(eleArea);
            var selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
          } else {
            eleArea.select();
          }
          // コピー
          document.execCommand('copy');
          // コピー用エレメントの削除
          //selection.removeAllRanges();
          $('#idForCopyElement').remove();
        }
        if (typeof (callback) == 'function') {
          callback();
        }

      } else {

        // コピーイベントが発生したら文書へのリンクをクリップボードにセット
        var _setToClipboard = function (e) {
          e.preventDefault();
          // IE
          if (Ext.isIE) {
            //window.clipboardData.setData(aFormat, aValue);
            window.clipboardData.setData('text', aValue);		// とりあえずtext固定
            // Chrome、FireFox、Edge
          } else {
            e.clipboardData.setData(aFormat, aValue);
          }
          // 文書へのリンクをクリップボードにセットする関数をコピーイベントから削除
          document.removeEventListener('copy', _setToClipboard, false);
          if (typeof (callback) == 'function') {
            callback();
          }
        };
        document.addEventListener('copy', _setToClipboard, false);
        // コピーイベントをキック
        document.execCommand('copy');
      }
    },

    /**
     * formatSizeUnits
     *
     * @param bytes
     * @returns {string}
     */
    formatSizeUnits: function (bytes) {
      if (bytes >= 1073741824) {
        bytes = (bytes / 1073741824).toFixed(2) + " GB";
      } else if (bytes >= 1048576) {
        bytes = (bytes / 1048576).toFixed(2) + " MB";
      } else if (bytes >= 1024) {
        bytes = (bytes / 1024).toFixed(2) + " KB";
      } else if (bytes > 1) {
        bytes = bytes + " bytes";
      } else if (bytes == 1) {
        bytes = bytes + " byte";
      } else {
        bytes = "0 bytes";
      }
      return bytes;
    },

    /**
     * validateEmail
     *
     * @param emailAddress
     * @returns {boolean}
     */
    validateEmail: function (emailAddress) {
      return Constants.REGEX_EMAIL.test(emailAddress);
    },

    /**
     * isNumber
     *
     * @param {string|number} number
     * @returns {boolean}
     */
    isNumber: function (number) {
      return Constants.REGEX_NUMBER.test(number);
    },

    /**
     * strToInt
     *
     * @param {string} strNumber
     * @returns {number}
     */
    strToInt: function (strNumber) {
      return parseInt(strNumber);
    },

    /**
     * formatMoney
     *
     * @param {number|string} value
     * @returns {string}
     */
    formatMoney: function (value) {
      if (!value || value == '' || typeof (value) == 'undefined') return 0;
      return new Intl.NumberFormat(Constants.LOCALES).format(MyUtil.strToInt(value));
    },

    convertTextSearch: function (valueConvert) {
      var value = Ext.clone(valueConvert);

      if (typeof (value) == 'string') {
        value = value.trim()
                     .replaceAll('(', '')
                     .replaceAll(')', '');

        // Replace key search have special characters
        var specialCharacters = ['\/', '\\', '~', '(', ')', '"'];
        for (var i = 0; i < specialCharacters.length; i++) {
          value = value.replaceAll(specialCharacters[i], '\x5C' + specialCharacters[i]);
        }

        value.replaceAll('[', '');
        value.replaceAll(']', '');
      }

      return value;
    },

    randomBetween: function (from, to) {
      return Math.floor(Math.random() * to) + from;
    },

    noneToZeroStr: function(string_param){
      if (string_param == null || typeof(string_param) == 'undefined') {
        return '';
      }

      return string_param;
    }
  };

  DisplayMgr = {
    /**
     * adjustByViewportWidth
     *
     * 幅の大きさをビューポートの幅と比較し、大きすぎたらビューポートの幅を返す
     *
     * @param {number} aWidth
     * @return {number} aWidthがビューポートの幅より大きい場合、ビューポートの幅を返す
     */
    adjustByViewportWidth: function (aWidth) {
      var retWidth = aWidth;

      Ext.ComponentMgr.getAll().each(function (aComponent) {
        if (aComponent.isXType('viewport')) {
          if (aComponent.getWidth() < aWidth) {
            retWidth = aComponent.getWidth();
            return false;
          }
        }
      });

      return retWidth;
    },

    /**
     * adjustByViewportHeight
     *
     * 高さパラメータをビューポートの高さと比較し、大きすぎたらビューポートの高さを返す
     *
     * @param {number} aHeight
     * @return aHeightがビューポートの高さより大きい場合、ビューポートの高さを返す
     */
    adjustByViewportHeight: function (aHeight) {
      var retHeight = aHeight;

      Ext.ComponentMgr.getAll().each(function (aComponent) {
        if (aComponent.isXType('viewport')) {
          if (aComponent.getHeight() < aHeight) {
            retHeight = aComponent.getHeight();
            return false;
          }
        }
      });

      return retHeight;
    },

    /**
     * getPriorityName
     *
     * @param {string} aPriority
     * @return {string}
     */
    getPriorityName: function (aPriority) {
      if (MyLang.getLocale() == 'ja') {
        if (aPriority == 'urgent') {
          return MyLang.getMsg('PRIORITY_URGENT');
        } else if (aPriority == 'normal') {
          return MyLang.getMsg('PRIORITY_USUALLY');
        } else {
          return aPriority;
        }
      } else {
        return aPriority;
      }
    },

    /**
     * setUnreadBold
     *
     * 太字フラグが立っていれば、太字で返す
     *
     * @param {string} aEscapedContentsHtml
     * @param {string} aDocId
     * @param {boolean} aBold
     * @param {string} aDummyForSort(optional)
     */
    setUnreadBold: function (aEscapedContentsHtml, aDocId, aBold, aDummyForSort) {
      if (typeof (aDummyForSort) == 'undefined') {
        aDummyForSort = aEscapedContentsHtml;
      }

      if (aBold) {
        return '<span dummy_for_sort="' + aDummyForSort + '" doc_id="' + aDocId + '" class="unread_doc">' + aEscapedContentsHtml + '</span>';
      }
      return '<span dummy_for_sort="' + aDummyForSort + '" doc_id="' + aDocId + '" >' + aEscapedContentsHtml + '</span>';
    },

    /**
     * boolToPublishWord
     *
     * @param {boolean} aIsPublished
     */
    boolToPublishWord: function (aIsPublished) {
      if (aIsPublished) {
        return '公開';
      }
      return '非公開';
    },

    /**
     * toSpanWithTitle
     *
     * @param {string} aName
     * @param {string} aEmail
     */
    toSpanWithTitle: function (aName, aEmail) {
      if (aName == null) {
        aName = '';
      }
      if (aEmail == null) {
        aEmail = '';
      }
      return '<span dummy_for_sort="' + aName + '" title="' + aEmail + '">' + aName + '</span>';
    },

    /**
     * toOpenLinkWithTitle
     *
     * @param {string} aName
     * @param {string} aEmail
     */
    toOpenLinkWithTitle: function (aName, aEmail) {
      if (aName == null) {
        aName = '';
      }
      if (aEmail == null) {
        aEmail = '';
      }
      var url = 'https://mail.google.com/a/' + LoginMgr.viewerEmail.split('@')[1] + '/?view=cm&fs=1&tf=1&su=&to=' + encodeURI(aEmail);
      var html = '';
      html += '<span dummy_for_sort="' + aName + '" title="' + aEmail + '">';
      html += '<a target="_blank" href="' + url + '">' + aName + '</a>';
      html += '</span>';
      return html;
    },
    /**
     * openPopup
     *
     * @param {String} aUrl
     */
    openPopup: function (aUrl) {
      var popup = window.open(aUrl, MyLang.getMsg('SIGN_IN'));
      // Check every 1000 ms if the popup is closed.
      finishedInterval = setInterval(function () {
        console.log('setInterval(function () {')
        // If the popup is closed, we've either finished OpenID, or the user closed it. Verify with the server in case the
        // user closed the popup.
        if (popup.closed) {
          LoginMgr.checkUser(SATERAITO_MY_SITE_URL, SATERAITO_GOOGLE_APPS_DOMAIN);
          clearInterval(finishedInterval);
        }
      }, 1000);
    },

    /**
     * openPopup2
     *
     * ポップアップの全画面ウィンドウを表示し、閉じられたときにコールバックをキックする
     *
     * @param {String} aUrl
     * @param {function} callback
     */
    openPopup2: function (aUrl, callback) {
      var popup = window.open(aUrl);
      // Check every 1000 ms if the popup is closed.
      finishedInterval = setInterval(function () {
        console.log('setInterval(function () {')
        // If the popup is closed, we've either finished OpenID, or the user closed it. Verify with the server in case the
        // user closed the popup.
        if (popup.closed) {
          clearInterval(finishedInterval);

          // SameSite対応…標準高速化対応のついでに自動リロード対応を追加 2019.12.30
          if (typeof (URL_TO_GO_AFTER_OIDC_LOGIN) != 'undefined' && URL_TO_GO_AFTER_OIDC_LOGIN != '') {
            window.location.href = URL_TO_GO_AFTER_OIDC_LOGIN;
          } else {
            parent.location.reload();
          }

          callback();
        }
      }, 1000);
    },

    /**
     * iOS13サードパーティーCookieブロック対策 2019.09.26
     * openPopup3
     *
     * @param {String} aUrl
     */
    openPopup3: function (aUrl) {
      var popup = window.open(aUrl, MyLang.getMsg('SIGN_IN'));
      // Check every 1000 ms if the popup is closed.
      finishedInterval = setInterval(function () {
        // If the popup is closed, we've either finished OpenID, or the user closed it. Verify with the server in case the
        // user closed the popup.
        if (popup.closed) {
          //LoginMgr.checkUser(SATERAITO_MY_SITE_URL, SATERAITO_GOOGLE_APPS_DOMAIN);
          document.write(MyLang.getMsg('RELOAD_THIS_PAGE_FOR_REAUTH'));
          clearInterval(finishedInterval);
          // ダメもとで親ページをリロードしてみる（ブロックされるだろうけど）自分自身のリロードはURLが違うのでNG。自身のiframeのsrcが取れればいいのだけどとれない...

          // SameSite対応…標準高速化対応のついでに自動リロード対応を追加 2019.12.30
          if (typeof (URL_TO_GO_AFTER_OIDC_LOGIN) != 'undefined' && URL_TO_GO_AFTER_OIDC_LOGIN != '') {
            window.location.href = URL_TO_GO_AFTER_OIDC_LOGIN;
          } else {
            parent.location.reload();
          }
        }
      }, 1000);
    },

    /**
     * openPopupOid
     *
     */
    openPopupOid: function () {
      var popup = window.open(POPUP_URL, MyLang.getMsg('SIGN_IN'));
      // Check every 1000 ms if the popup is closed.
      finishedInterval = setInterval(function () {
        console.log('setInterval(function () {')
        // If the popup is closed, we've either finished OpenID, or the user closed it. Verify with the server in case the
        // user closed the popup.
        if (popup.closed) {
          location.reload();
          // LoginMgr.checkUserOid(SATERAITO_MY_SITE_URL, SATERAITO_GOOGLE_APPS_DOMAIN);
          clearInterval(finishedInterval);
        }
      }, 1000);
    },

    /**
     * getIconCls
     *
     * ファイルのアイコンのClsを返す
     *
     * @param {string} aFileName
     */
    getIconCls: function (aFileName) {
      var fileNameSplited = aFileName.split('.');
      var numSplited = fileNameSplited.length;
      if (numSplited > 0) {
        var extension = ('' + fileNameSplited[numSplited - 1]).toLowerCase();
        switch (extension) {
          case 'txt':
            // return SATERAITO_MY_SITE_URL + '/images/icon_png/icon_10_text_list.png';
            return 'mdi mdi-file-document'
          case 'pdf':
            // return SATERAITO_MY_SITE_URL + '/images/icon_png/icon_10_pdf_list.png';
            return 'mdi mdi-file-pdf-box'
          case 'doc':
            // return SATERAITO_MY_SITE_URL + '/images/icon_png/icon_10_word_list.png';
            return 'mdi mdi-file-word-box'
          case 'docx':
            // return SATERAITO_MY_SITE_URL + '/images/icon_png/icon_10_word_list.png';
            return 'mdi mdi-file-word-box'
          case 'zip':
            // return SATERAITO_MY_SITE_URL + '/images/icon_png/icon_9_archive_list.png';
            return 'mdi mdi-zip-box'
          case 'rar':
            // return SATERAITO_MY_SITE_URL + '/images/icon_png/icon_9_archive_list.png';
            return 'mdi mdi-zip-box'
          case 'xls':
            // return SATERAITO_MY_SITE_URL + '/images/icon_png/icon_10_excel_list.png';
            return 'mdi mdi-file-excel-box'
          case 'xlsx':
            // return SATERAITO_MY_SITE_URL + '/images/icon_png/icon_10_excel_list.png';
            return 'mdi mdi-file-excel-box'
          case 'csv':
            // return SATERAITO_MY_SITE_URL + '/images/icon_png/icon_10_excel_list.png';
            return 'mdi mdi-file-excel-box'
          case 'ppt':
            // return SATERAITO_MY_SITE_URL + '/images/icon_png/icon_10_powerpoint_list.png';
            return 'mdi mdi-file-powerpoint-box'
          case 'pptx':
            // return SATERAITO_MY_SITE_URL + '/images/icon_png/icon_10_powerpoint_list.png';
            return 'mdi mdi-file-powerpoint-box'
          case 'png':
            // return SATERAITO_MY_SITE_URL + '/images/icon_png/icon_11_image_list.png';
            return 'mdi mdi-image'
          case 'jpg':
            // return SATERAITO_MY_SITE_URL + '/images/icon_png/icon_11_image_list.png';
            return 'mdi mdi-image'
          case 'jpeg':
            // return SATERAITO_MY_SITE_URL + '/images/icon_png/icon_11_image_list.png';
            return 'mdi mdi-image'
          case 'gif':
            // return SATERAITO_MY_SITE_URL + '/images/icon_png/icon_11_image_list.png';
            return 'mdi mdi-image'
          case 'mp4':
          case 'mpeg':
          case 'mov':
            return 'mdi mdi-file-video'
          case 'mp3':
          case 'mp2':
            return 'mdi mdi-music-box'
        }
      }
      return 'mdi mdi-file'
    },

    getExtensionFile: function (aFileName) {
      var fileNameSplited = aFileName.split('.');
      var numSplited = fileNameSplited.length;
      if (numSplited > 0) {
        return ('' + fileNameSplited[numSplited - 1]).toLowerCase();
      }
    },

    /**
     * toDownloadLink
     *
     * ファイル名をクリックしてファイルをダウンロードするリンクを生成する
     * アイコンも表示し、アイコンをクリックするとファイルの詳細が表示されるようにする
     *
     */
    toDownloadLink: function (aFileId, aFileName, aIsDownloadable, aFileSize, aAuthorEmail,
                              aAuthorName, aMimeType, aIconLink, aUploadedDate, aFolderCode, aAttachmentType, aAttachLink,
                              aTypeItem, aAttachmentId, aPublishFlag, aFileDeleted) {
      var downloadable = '0';
      if (aIsDownloadable) {
        downloadable = '1';
      }
      var fileNameSplited = ('' + aFileName).split('.');
      var isPdf = '0';
      if (fileNameSplited[fileNameSplited.length - 1].toLowerCase() == 'pdf') {
        isPdf = '1';
      }
      if (typeof (aPublishFlag) == 'undefined') {
        aPublishFlag = false;
      }
      if (typeof (aFileDeleted) == 'undefined') {
        aFileDeleted = false;
      }

      var vHtmlLink = '<div class="wrap-file-name d-flex align-items-center">';
      if (aAttachmentType == 'webattachment') {
        var iconCls = 'mdi mdi-link';

        if (aIconLink) {
          vHtmlLink += '<img dummy_for_sort="' + aFileName + '"';
          vHtmlLink += ' class="file_icon"';
          vHtmlLink += ' src="' + aIconLink + '"';
        } else {
          vHtmlLink += '<span dummy_for_sort="' + aFileName + '"';
          vHtmlLink += ' class="file_icon ' + iconCls + '"';
          vHtmlLink += ' icon-file-cls="' + iconCls + '"';
        }
        vHtmlLink += ' file_name="' + aFileName + '"';
        vHtmlLink += ' file_size="' + MyUtil.noneToZeroStr(aFileSize) + '"';
        vHtmlLink += ' author_email="' + MyUtil.noneToZeroStr(aAuthorEmail) + '"';
        vHtmlLink += ' author_name="' + MyUtil.noneToZeroStr(aAuthorName) + '"';
        vHtmlLink += ' mime_type="' + MyUtil.noneToZeroStr(aMimeType) + '"';
        vHtmlLink += ' kind_term="file"';
        vHtmlLink += ' uploaded_date="' + MyUtil.noneToZeroStr(aUploadedDate) + '"';
        if (aIsDownloadable) {
          vHtmlLink += ' download_link="' + MyUtil.noneToZeroStr(aAttachLink) + '"';
        }
        vHtmlLink += ' folder_code="' + MyUtil.noneToZeroStr(aFolderCode) + '"';
        vHtmlLink += ' type_item="' + MyUtil.noneToZeroStr(aTypeItem) + '"';
        vHtmlLink += ' publish_flag="' + MyUtil.noneToZeroStr(aPublishFlag) + '"';
        vHtmlLink += ' deleted_flag="' + MyUtil.noneToZeroStr(aFileDeleted) + '"';
        if (aIconLink) {
          vHtmlLink += ' style="vertical-align:middle;"/>';
        } else {
          vHtmlLink += ' style="vertical-align:middle;"> </span>';
        }

        if (aFileDeleted || !aIsDownloadable) {
          vHtmlLink += '<span class="link_cmd">';
        } else {
          vHtmlLink += '<span class="link_cmd" onclick="window.open(\'' + aAttachLink + '\');">';
        }
        vHtmlLink += Sateraito.Util.escapeHtml(aFileName);
        vHtmlLink += '</span>';
      } else {
        var iconCls = DisplayMgr.getIconCls(aFileName);
        if (aTypeItem == Constants.TYPE_FOLDER) {
          iconCls = 'mdi mdi-folder';
        }
        var showIconPreview = ((aTypeItem != Constants.TYPE_FOLDER) && !aFileDeleted && IS_PREVIEW && (aTypeItem != Constants.TYPE_ATTACH_EMAIL));

        if (aTypeItem == Constants.TYPE_FOLDER) {
          iconCls = 'mdi mdi-folder';
        }

        if (aIconLink) {
          vHtmlLink += '<img dummy_for_sort="' + aFileName + '"';
          vHtmlLink += ' class="file_icon"';
          vHtmlLink += ' src="' + aIconLink + '"';
        } else {
          vHtmlLink += '<span dummy_for_sort="' + aFileName + '"';
          vHtmlLink += ' class="file_icon ' + iconCls + '"';
          vHtmlLink += ' icon-file-cls="' + iconCls + '"';
        }
        vHtmlLink += ' file_name="' + MyUtil.noneToZeroStr(aFileName) + '"';
        vHtmlLink += ' file_size="' + MyUtil.noneToZeroStr(aFileSize) + '"';
        vHtmlLink += ' author_email="' + MyUtil.noneToZeroStr(aAuthorEmail) + '"';
        vHtmlLink += ' author_name="' + MyUtil.noneToZeroStr(aAuthorName) + '"';
        vHtmlLink += ' mime_type="' + MyUtil.noneToZeroStr(aMimeType) + '"';
        vHtmlLink += ' kind_term="file"';
        vHtmlLink += ' uploaded_date="' + MyUtil.noneToZeroStr(aUploadedDate) + '"';
        if (aIsDownloadable && aFileId) {
          vHtmlLink += ' download_link="' + SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/attach/oid/downloadattachedfile/' + aFileId + '"';
        }
        vHtmlLink += ' folder_code="' + MyUtil.noneToZeroStr(aFolderCode) + '"';
        vHtmlLink += ' type_item="' + MyUtil.noneToZeroStr(aTypeItem) + '"';
        vHtmlLink += ' publish_flag="' + MyUtil.noneToZeroStr(aPublishFlag) + '"';
        vHtmlLink += ' deleted_flag="' + MyUtil.noneToZeroStr(aFileDeleted) + '"';
        if (aIconLink) {
          vHtmlLink += ' style="vertical-align:middle;"/>';
        } else {
          vHtmlLink += ' style="vertical-align:middle;"></span>';
        }

        vHtmlLink += '<div class="file-name">';
        vHtmlLink += '<div class="link_cmd download_attached_file" deleted_flag="' + MyUtil.noneToZeroStr(aFileDeleted) + '" attachment_id="' + MyUtil.noneToZeroStr(aAttachmentId) + '"';
        vHtmlLink += '      file_id="' + MyUtil.noneToZeroStr(aFileId) + '" file_name="' + MyUtil.noneToZeroStr(aFileName) + '" mime_type="' + MyUtil.noneToZeroStr(aMimeType) + '" file_size="' + MyUtil.noneToZeroStr(aFileSize) + '"';
        vHtmlLink += '      type_item="' + MyUtil.noneToZeroStr(aTypeItem) + '" downloadable="' + downloadable + '" is_preview="' + showIconPreview + '"';
        vHtmlLink += '>';
        vHtmlLink +=    Sateraito.Util.escapeHtml(aFileName);
        vHtmlLink += '</div>';

        if (showIconPreview && aIsDownloadable) {
          vHtmlLink += '<span title="' + MyLang.getMsg('ATTACHED_FILE_PREVIEW') + '" is_image="' + FileflowDocManager.isImageFile(aFileName) + '" is_pdf="' + isPdf + '" onclick="FileflowDocManager.openGoogleDocViewer(this);" file_id="' + aFileId + '" class="preview-icon mdi mdi-image-search-outline">';
          vHtmlLink += '</span>';
        }
        vHtmlLink += '</div>';
      }
      vHtmlLink += '</div>';


      return vHtmlLink
    },

    /**
     * toAdminDownloadLink
     *
     * ファイルをダウンロードするリンクを返す（アドミン用）
     *
     */
    toAdminDownloadLink: function (aFileId, aFileName, aIsDownloadable, aFileSize, aAuthorEmail,
                                   aAuthorName, aMimeType, aIconLink, aUploadedDate, aFolderCode, aAttachmentType, aAttachLink,
                                   aTypeItem, aAttachmentId, aPublishFlag, aFileDeleted) {
      var downloadable = '1';
      var vHtmlLink = '<div class="wrap-file-name d-flex align-items-center">';
      var iconCls = DisplayMgr.getIconCls(aFileName);
      if (typeof (aPublishFlag) == 'undefined') {
        aPublishFlag = false;
      }
      if (typeof (aFileDeleted) == 'undefined') {
        aFileDeleted = false;
      }
      var fileNameSplited = ('' + aFileName).split('.');
      var isPdf = '0';
      if (fileNameSplited[fileNameSplited.length - 1].toLowerCase() == 'pdf') {
        isPdf = '1';
      }

      if (aAttachmentType == 'webattachment') {
        var iconCls = 'mdi mdi-link';

        if (aIconLink) {
          vHtmlLink += '<img dummy_for_sort="' + aFileName + '"';
          vHtmlLink += ' class="file_icon"';
          vHtmlLink += ' src="' + aIconLink + '"';
        } else {
          vHtmlLink += '<span dummy_for_sort="' + aFileName + '"';
          vHtmlLink += ' class="file_icon ' + iconCls + '"';
          vHtmlLink += ' icon-file-cls="' + iconCls + '"';
        }
        vHtmlLink += ' file_name="' + aFileName + '"';
        vHtmlLink += ' file_size="' + MyUtil.noneToZeroStr(aFileSize) + '"';
        vHtmlLink += ' author_email="' + MyUtil.noneToZeroStr(aAuthorEmail) + '"';
        vHtmlLink += ' author_name="' + MyUtil.noneToZeroStr(aAuthorName) + '"';
        vHtmlLink += ' mime_type="' + MyUtil.noneToZeroStr(aMimeType) + '"';
        vHtmlLink += ' kind_term="file"';
        vHtmlLink += ' uploaded_date="' + MyUtil.noneToZeroStr(aUploadedDate) + '"';
        vHtmlLink += ' download_link="' + MyUtil.noneToZeroStr(aAttachLink) + '"';
        vHtmlLink += ' folder_code="' + MyUtil.noneToZeroStr(aFolderCode) + '"';
        vHtmlLink += ' type_item="' + MyUtil.noneToZeroStr(aTypeItem) + '"';
        vHtmlLink += ' publish_flag="' + MyUtil.noneToZeroStr(aPublishFlag) + '"';
        vHtmlLink += ' deleted_flag="' + MyUtil.noneToZeroStr(aFileDeleted) + '"';
        if (aIconLink) {
          vHtmlLink += ' style="vertical-align:middle;"/>';
        } else {
          vHtmlLink += ' style="vertical-align:middle;"> </span>';
        }

        if (aFileDeleted) {
          vHtmlLink += '<span class="link_cmd">';
        } else {
          vHtmlLink += '<span class="link_cmd" onclick="window.open(\'' + aAttachLink + '\');">';
        }
        vHtmlLink += Sateraito.Util.escapeHtml(aFileName);
        vHtmlLink += '</span>';
      } else {
        var iconCls = DisplayMgr.getIconCls(aFileName);
        var showIconPreview = ((aTypeItem != Constants.TYPE_FOLDER) && IS_PREVIEW && (aTypeItem != Constants.TYPE_ATTACH_EMAIL));
        if (aTypeItem == Constants.TYPE_FOLDER) {
          iconCls = 'mdi mdi-folder';
        }

        if (aIconLink) {
          vHtmlLink += '<img dummy_for_sort="' + aFileName + '"';
          vHtmlLink += ' class="file_icon"';
          vHtmlLink += ' src="' + aIconLink + '"';
        } else {
          vHtmlLink += '<span dummy_for_sort="' + aFileName + '"';
          vHtmlLink += ' class="file_icon ' + iconCls + '"';
          vHtmlLink += ' icon-file-cls="' + iconCls + '"';
        }
        vHtmlLink += ' file_name="' + aFileName + '"';
        vHtmlLink += ' file_size="' + MyUtil.noneToZeroStr(aFileSize) + '"';
        vHtmlLink += ' author_email="' + MyUtil.noneToZeroStr(aAuthorEmail) + '"';
        vHtmlLink += ' author_name="' + MyUtil.noneToZeroStr(aAuthorName) + '"';
        vHtmlLink += ' mime_type="' + MyUtil.noneToZeroStr(aMimeType) + '"';
        vHtmlLink += ' kind_term="file"';
        vHtmlLink += ' uploaded_date="' + MyUtil.noneToZeroStr(aUploadedDate) + '"';
        vHtmlLink += ' download_link="' + SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/attach/oid/downloadattachedfile/' + aFileId + '"';
        vHtmlLink += ' folder_code="' + MyUtil.noneToZeroStr(aFolderCode) + '"';
        vHtmlLink += ' type_item="' + MyUtil.noneToZeroStr(aTypeItem) + '"';
        vHtmlLink += ' publish_flag="' + MyUtil.noneToZeroStr(aPublishFlag) + '"';
        vHtmlLink += ' deleted_flag="' + MyUtil.noneToZeroStr(aFileDeleted) + '"';
        if (aIconLink) {
          vHtmlLink += ' style="vertical-align:middle;"/>  &nbsp;';
        } else {
          vHtmlLink += ' style="vertical-align:middle;"> </span> &nbsp;';
        }


        vHtmlLink += '<div class="file-name">';
        vHtmlLink += '<div class="link_cmd download_attached_file_admin" deleted_flag="' + MyUtil.noneToZeroStr(aFileDeleted) + '" attachment_id="' + MyUtil.noneToZeroStr(aAttachmentId) + '"';
        vHtmlLink += '      file_id="' + MyUtil.noneToZeroStr(aFileId) + '" file_name="' + MyUtil.noneToZeroStr(aFileName) + '" mime_type="' + MyUtil.noneToZeroStr(aMimeType) + '" file_size="' + MyUtil.noneToZeroStr(aFileSize) + '"';
        vHtmlLink += '      type_item="' + MyUtil.noneToZeroStr(aTypeItem) + '" downloadable="' + downloadable + '" is_preview="' + showIconPreview + '"';
        vHtmlLink += '>';
        vHtmlLink +=    Sateraito.Util.escapeHtml(aFileName);
        vHtmlLink += '</div>';

        if (showIconPreview) {
          vHtmlLink += '<span title="' + MyLang.getMsg('ATTACHED_FILE_PREVIEW') + '" is_image="' + FileflowDocManager.isImageFile(aFileName) + '" is_pdf="' + isPdf + '" onclick="FileflowDocManager.openGoogleDocViewer(this);" file_id="' + aFileId + '" class="preview-icon mdi mdi-image-search-outline">';
          vHtmlLink += '</span>';
        }
        vHtmlLink += '</div>';
      }
      vHtmlLink += '</div>';

      return vHtmlLink
    },

    /**
     * toMailLink
     *
     * メール作成画面を開くリンクを返す
     * メールアドレスでない場合、リンクにしないで返す
     *
     * @param {string} aUserEmail
     * @param {string} aUserName
     */
    toMailLink: function (aUserEmail, aUserName, isShowUserName) {
      if (aUserEmail == null || aUserEmail == '' || typeof (aUserEmail) == 'undefined') {
        return '';
      }

      if (!Sateraito.Util.isMailAddress(aUserEmail)) {
        return aUserEmail;
      }

      var linkHtml = '';
      linkHtml += '<a dummy_for_sort="' + aUserEmail + '" href="';
      if (Sateraito.Util.isSmartPhone()) {
        linkHtml += 'https://mail.google.com/mail/mu/mp/333/#co/to=';
      } else {
        linkHtml += 'https://mail.google.com/a/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/?view=cm&fs=1&tf=1&su=&to=';
      }
      if (aUserName == '' || Sateraito.Util.isMailAddress(aUserName)) {
        linkHtml += encodeURI(aUserEmail);
      } else {
        linkHtml += encodeURI('"' + aUserName + '" <' + aUserEmail + '>');
      }
      linkHtml += '"';
      linkHtml += ' target="_blank"';
      linkHtml += ' style="cursor:pointer;"';
      linkHtml += ' title="' + MyLang.getMsg('OPEN_MAIL_WINDOW') + '"';
      linkHtml += '>';
      if (isShowUserName && aUserName.trim() != '') {
        linkHtml += aUserName;
      } else {
        linkHtml += aUserEmail;
      }
      linkHtml += '</a>';
      return linkHtml;
    },

    /**
     * bindFileIconEventHandler
     *
     * ファイルアイコンをクリックした時のイベントハンドラをバインドする
     */
    bindFileIconEventHandler: function () {
      $(document).on('click', 'span.file_icon, img.file_icon', function () {
        // ファイルアイコンクリック時のイベント
        var element = this;

        var deletedFlag = $(element).attr('deleted_flag');
        if (Sateraito.Util.strToBool(deletedFlag)) {
          if (MyPanel.nameScreen != Constants.SCREEN_ADMIN_CONSOLE) {
            return
          }
        }

        if ($(element).attr('type_item') == Constants.TYPE_FILE) {
          DisplayMgr.showFileDetailWindow(element);
        }
      });
    },

    /**
     * showFileDetailWindow
     *
     * ファイル詳細ウィンドウを開く
     *
     * @param {Object} element
     */
    showFileDetailWindow: function (element) {
      var folderCode = $(element).attr('folder_code');
      if (typeof (folderCode) == 'undefined' || folderCode == null || folderCode == '') {
        DisplayMgr._showFileDetailWindow(element, '');
      } else {
        DocFolderRequest.requestFolderNameFullpathPath(folderCode, function (aJsondata) {
          DisplayMgr._showFileDetailWindow(element, aJsondata.folder_name_fullpath);
        });
      }
    },

    /**
     * _showFileDetailWindow
     *
     * @param {object} element
     * @param {string} aFolderNameFullpath
     */
    _showFileDetailWindow: function (element, aFolderNameFullpath) {
      var vHtml = '';
      vHtml += '<div style="padding:10px;">';
      vHtml += '<table class="layout" style="width:99%">';

      // ファイル名
      var iconFileCls = $(element).attr('icon-file-cls');
      var iconFileSrc = $(element).attr('src');
      vHtml += '<tr class="layout">';
      vHtml += '<td class="layout">';
      vHtml += MyLang.getMsg('FILE_NAME');
      vHtml += '</td>';
      vHtml += '<td class="layout">';
      if (iconFileSrc) {
        vHtml += '<img src="' + iconFileSrc + '"> &nbsp;';
      } else {
        vHtml += '<span class="' + iconFileCls + '"></span> &nbsp;';
      }
      vHtml += $(element).attr('file_name');
      vHtml += '</td>';
      vHtml += '</tr>';

      // ファイルサイズ
      var fileSize = $(element).attr('file_size');
      if (typeof (fileSize) == 'undefined' || fileSize == null || fileSize == '' || fileSize == '0') {
        // no operation
        // Googleドライブの場合、GoogleスプレッドシートやGoogle文書はサイズ0で返ってくる
      } else {
        if (isNaN(fileSize)) {
          // no operation
        } else {
          vHtml += '<tr class="layout">';
          vHtml += '<td class="layout">';
          vHtml += MyLang.getMsg('FILE_SIZE');
          vHtml += '</td>';
          vHtml += '<td class="layout">';
          vHtml += MyUtil.formatSizeUnits(fileSize) + ' (' + NumUtil.addComma(fileSize) + ' Byte)';
          vHtml += '</td>';
          vHtml += '</tr>';
        }
      }

      // 作成者メールアドレス、作成者名
      var authorName = $(element).attr('author_name');
      var authorEmail = $(element).attr('author_email');
      if (typeof (authorName) == 'undefined' || authorName == null || authorName == '') {
        // no operation
      } else {
        vHtml += '<tr class="layout">';
        vHtml += '<td class="layout">';
        vHtml += MyLang.getMsg('AUTHOR_NAME');
        vHtml += '</td>';
        vHtml += '<td class="layout">';
        vHtml += authorName;
        vHtml += '</td>';
        vHtml += '</tr>';
      }
      if (typeof (authorEmail) == 'undefined' || authorEmail == null || authorEmail == '') {
        // no operation
      } else {
        vHtml += '<tr class="layout">';
        vHtml += '<td class="layout">';
        vHtml += MyLang.getMsg('AUTHOR_EMAIL');
        vHtml += '</td>';
        vHtml += '<td class="layout">';
        vHtml += DisplayMgr.toMailLink(authorEmail, authorName);
        vHtml += '</td>';
        vHtml += '</tr>';
      }

      // MIMEタイプ/種別
      var mimeType = $(element).attr('mime_type');
      var kindTerm = $(element).attr('kind_term');
      if (kindTerm == 'file') {
        vHtml += '<tr class="layout">';
        vHtml += '<td class="layout">';
        vHtml += MyLang.getMsg('MIME_TYPE');
        vHtml += '</td>';
        vHtml += '<td class="layout">';
        vHtml += mimeType;
        vHtml += '</td>';
        vHtml += '</tr>';
      } else {
        vHtml += '<tr class="layout">';
        vHtml += '<td class="layout">';
        vHtml += MyLang.getMsg('KIND_TERM');
        vHtml += '</td>';
        vHtml += '<td class="layout">';
        if (kindTerm == 'spreadsheet') {
          vHtml += MyLang.getMsg('GOOGLE_SPREADSHEET');
        } else if (kindTerm == 'document') {
          vHtml += MyLang.getMsg('GOOGLE_DOCUMENT');
        } else if (kindTerm == 'presentation') {
          vHtml += MyLang.getMsg('GOOGLE_PRESENTATION');
        } else if (kindTerm == 'drawing') {
          vHtml += MyLang.getMsg('GOOGLE_DRAWING');
        } else if (kindTerm == 'form') {
          vHtml += MyLang.getMsg('GOOGLE_FORM');
        } else {
          vHtml += kindTerm;
        }
        vHtml += '</td>';
        vHtml += '</tr>';
      }

      // 作成日時
      var uploadedDate = $(element).attr('uploaded_date');
      if (typeof (uploadedDate) == 'undefined' || uploadedDate == null || uploadedDate == '') {
        // no operation
      } else {
        vHtml += '<tr class="layout">';
        vHtml += '<td class="layout">';
        vHtml += MyLang.getMsg('UPLOADED_DATE');
        vHtml += '</td>';
        vHtml += '<td class="layout">';
        vHtml += uploadedDate;
        vHtml += '</td>';
        vHtml += '</tr>';
      }

      // ファイルへのリンク
      var downloadLink = $(element).attr('download_link');
      if (typeof (downloadLink) == 'undefined' || downloadLink == null || downloadLink == '') {
        // no operation
      } else {
        vHtml += '<tr class="layout">';
        vHtml += '<td class="layout">';
        vHtml += MyLang.getMsg('LINK_TO_THIS_FILE_MAIL');
        vHtml += '</td>';
        vHtml += '<td class="layout">';
        vHtml += '<input type="text" value="' + downloadLink + '" onclick="this.select(0,this.value.length)" style="width:100%;">';
        vHtml += '</td>';
        vHtml += '</tr>';
      }

      // カテゴリー
      if (typeof (aFolderNameFullpath) == 'undefined' || aFolderNameFullpath == null || aFolderNameFullpath == '') {
        // no operation
      } else {
        vHtml += '<tr class="layout">';
        vHtml += '<td class="layout">';
        vHtml += OtherSetting.wordingForFolder;
        vHtml += '</td>';
        vHtml += '<td class="layout">';
        var googleDriveFolderNamePath = $(element).attr('google_drive_folder_name_path');
        if (typeof (googleDriveFolderNamePath) == 'undefined' || googleDriveFolderNamePath == null || googleDriveFolderNamePath == '') {
          vHtml += aFolderNameFullpath;
        } else {
          vHtml += aFolderNameFullpath + '/' + googleDriveFolderNamePath;
        }
        vHtml += '</td>';
        vHtml += '</tr>';
      }

      vHtml += '</table>';
      vHtml += '</div>';

      var detailPanel = {
        xtype: 'panel',
        autoWidth: true,
        scrollable: true,
        html: vHtml
      };

      var detailWindow = new Ext.Window({
        id: 'file_detail_window',
        width: DisplayMgr.adjustByViewportWidth(500),
        height: DisplayMgr.adjustByViewportHeight(300),
        title: MyLang.getMsg('FILE_DETAIL'),
        plain: true,
        autoScroll: false,
        layout: 'fit',
        modal: true,
        items: [detailPanel]
      });

      // ウィンドウを表示
      detailWindow.show();
    },

    toVHtmlTag: function (listTag) {
      var vHtml = '';
      for (var i = 0; i < listTag.length; i++) {
        var text = listTag[i].trim();
        if (text != '') {
          vHtml += '<span class="chips-tag">#' + text + '</span>';
        }
      }
      return vHtml;
    },

    /**
     * toConvertDescription
     *
     * @param {string} description
     * @returns {string}
     */
    toConvertDescription: function (description) {
      return description.replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('\n', '<br/>');
    },

    toNameHtml: function (name, type) {
      if (type == Constants.TYPE_FOLDER) {
        return '<span class="mdi mdi-folder"></span> <span>' + name + '</span>';
      } else {
        return '<span class="' + DisplayMgr.getIconCls(name) + '"></span> <span>' + name + '</span>';
      }
    },

    toTextFolderHtml: function (record) {
      var folderCode = record.folder_code;
      var folderName = record.folder_name;
      var parentFolderCode = record.parent_folder_code;

      var vHtml = '';
      vHtml += '<span class="link_cmd2" onclick="FolderDetailWindow.showWindow(\'' + folderCode + '\', null, FolderMaintePanel.buildFolderTree, true);">';
      vHtml += folderName;
      vHtml += '</span>';
      vHtml += ' <span style="color:blue;" onclick="FolderDetailWindow.showWindow(\'__new_folder\',\'' + folderCode + '\', FolderMaintePanel.buildFolderTree, true);">';
      vHtml += MyLang.getMsg('ADD_CHILD_SOMETHING').replace(/%1/g, OtherSetting.wordingForFolder);
      vHtml += '</span>';

      return vHtml;
    },

    /**
     * openPopupOidAddOn
     *
     */
    openPopupOidAddOn: function () {
      var popup = window.open(POPUP_URL, MyLang.getMsg('SIGN_IN'));
      // Check every 1000 ms if the popup is closed.
      finishedInterval = setInterval(function () {
        console.log('setInterval(function () {')
        // If the popup is closed, we've either finished OpenID, or the user closed it. Verify with the server in case the
        // user closed the popup.
        if (popup.closed) {
          clearInterval(finishedInterval);
          window.location.reload();
        }
      }, 1000);
    },

    handlerWindowSelectTypeUpload: function (callback) {
      // ウィンドウインスタンスを作成
      var detailWindow = new Ext.Window({
        width: 0,
        height: DisplayMgr.adjustByViewportHeight(100),
        title: MyLang.getMsg('PLEASE_SELECT_TYPE_UPLOAD_FILE_FOR_DOC'),
        modal: true,
        maximizable: false,
        // resizable: false,
        bodyStyle: 'background-color:white;',
        plain: true,
        scrollable: false,
        padding: 5,
        layout: {
          type: 'hbox',
          align: 'center'
        },
        items: [
          {
            xtype: 'button',
            width: '15rem',
            height: 50,
            margin: '0 5px 0 0',
            iconCls: 'mdi mdi-pencil-box-outline',
            text: MyLang.getMsg('CREATE_WORKFLOW_DOC_FILE_FROM_LOCAL'),
            handler: function () {
              callback(Constants.KEY_SELECT_FILE_FROM_LOCAL);
              detailWindow.close();
            }
          },
          {
            xtype: 'button',
            width: '15rem',
            height: 50,
            // margin: '0 0 0 0px',
            icon: SATERAITO_MY_SITE_URL + "/images/drive.png",
            text: MyLang.getMsg('CREATE_WORKFLOW_DOC_FILE_FROM_GOOGLE_DRIVE'),
            handler: function () {
              callback(Constants.KEY_SELECT_FILE_FROM_GOOGLE_DRIVE);
              detailWindow.close();
            }
          }
        ],
        listeners: {
          afterrender: function (dialogCmp) {
            Ext.defer(function () {
              var maxWith = 17;
              for (var i = 0; i < dialogCmp.items.getCount(); i++) {
                maxWith += dialogCmp.items.getAt(i).getWidth();
              }

              dialogCmp.setWidth(maxWith);
              dialogCmp.center();
            }, 10);
          }
        }
      });

      // ウィンドウを開く
      detailWindow.show();
    },

    getNameTypeOperation: function (key_name) {
      switch (key_name) {
        case 'download_file':
          return MyLang.getMsg('TXT_DOWNLOAD_FILE')
        case 'upload_file':
          return MyLang.getMsg('TXT_UPLOAD_FILE')
        case 'delete_file':
          return MyLang.getMsg('TXT_DELETE_FILE')
        case 'create_folder':
          return MyLang.getMsg('TXT_CREATE_FOLDER')
        case 'update_folder':
          return MyLang.getMsg('TXT_UPDATE_FOLDER')
        case 'delete_folder':
          return MyLang.getMsg('TXT_DELETE_FOLDER')
        case 'create_workflow_doc':
          return MyLang.getMsg('TXT_CREATE_DOC')
        case 'update_workflow_doc':
          return MyLang.getMsg('TXT_UPDATE_DOC')
        case 'delete_workflow_doc':
          return MyLang.getMsg('TXT_DELETE_DOC')
        default:
          return 'undefined: ' + key_name
      }
    },

    getNameScreen: function (key_screen) {
      switch (key_screen) {
        case 'admin':
        case 'admin_console':
          return MyLang.getMsg('ADMIN_CONSOLE')
        case 'user_console':
          return MyLang.getMsg('USER_CONSOLE')
        case 'direct_link':
          return MyLang.getMsg('DIRECT_LINK')
        case 'popup_file_upload':
        case 'upload gmail':
          return MyLang.getMsg('PLUGIN_FILE_UPLOAD')
        default:
          return 'undefined: ' + key_screen
      }
    },

    toTitleDocDisplay: function (record, key_filter_doc_deleted) {
      if (typeof(key_filter_doc_deleted) == 'undefined' || !key_filter_doc_deleted) {
        key_filter_doc_deleted = Constants.KEY_FILTER_DELETED_DOC;
      }

      var img_popup ='';
          img_popup += '<span class="detail_popup cursor-pointer mdi mdi-open-in-new" onclick="';
          img_popup += 'var option = {};';
          img_popup += 'DetailDocPopup.showPopupDetail(\'' + record.workflow_doc_id + '\', \'' + key_filter_doc_deleted + '\' , option);';
          img_popup += '"></span>';
          img_popup += '<span class="link_cmd2">' + record.title + '</span>';

      return img_popup;
    },
  };

  /**
   * SameSite対応の一環…高速化を標準とする対応：Oidc認証チェック関連. ログインステータスチェック対応 2016.12.20
   */
  OidcUtil = {

    setCheckCurrentUserTimestamp: function () {
      Ext.util.Cookies.set('checkcurrentusertimestamp', Date.now());
    },

    getCheckCurrentUserTimestamp: function () {
      return Ext.util.Cookies.get('checkcurrentusertimestamp');
    },

    // ログインステータスチェック対応 2016.12.08
    signOutAndShowOidcReSigninMessage: function (popup) {
      Sateraito.Util.console('signOutAndShowOidcReSigninMessage...');
      // URLを変更したくないのでこのページ自体で認証リンクを表示 2019.12.20
      //// ログアウト処理後画面上にメッセージを表示
      var vHtml = '';
      vHtml += '<div class="message">';
      vHtml += MyLang.getMsg('EXP_OIDC_RE_SIGNIN');
      vHtml += '<br/>';
      vHtml += '<p>';
      vHtml += '<a href="javascript:void(0);" onclick="DisplayMgr.openPopup2(\'' + popup + '\');">';
      vHtml += MyLang.getMsg('CLICK_HERE_TO_SIGN_IN');
      vHtml += '</a>';
      vHtml += '</p>';

      vHtml += '</div>';

      Ext.select('#output').update(vHtml);

      // リロードしてみる（iframeの場合はブロックされるだろうけど）
      if (typeof (window.parent) != 'undefined') {
        parent.location.reload();
      } else {
        location.reload();
      }
    },

    // 初回チェック用iframe
    startCheckOidcCurrentUser: function () {
      // 5分以内にキックされていた場合は、５分遅らせてキックする（O365版の対応だが一応入れておく）
      var lastStartedTimestamp = OidcUtil.getCheckCurrentUserTimestamp();
      Sateraito.Util.console('lastStartedTimestamp=' + lastStartedTimestamp);
      var kick5minLater = false;
      if (lastStartedTimestamp != null) {
        var interval = Date.now() - lastStartedTimestamp;
        if (interval < 1000 * 60 * 5) {
          kick5minLater = true;
        }
      }

      if (kick5minLater) {
        var randomFactor = Math.ceil(Math.random() * 1000);  // 複数ガジェットがある場合タイミングがぴったりあわないようランダムを加える
        (function () {
          OidcUtil.startCheckOidcCurrentUser();
        }).defer(1000 * 60 * 5 + randomFactor);
      } else {
        OidcUtil.setCheckCurrentUserTimestamp();
        Sateraito.Util.console('startCheckOidcCurrentUser...');
        var vHtml = '';
        vHtml += '<iframe id="ck_iframe" src="' + SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/oidccheckcurrentuser"';
        vHtml += ' style="width:0%;height:0%;display:none;">';
        vHtml += '</iframe>';
        $('body').append(vHtml);
      }
    }
  };

  /**
   * ガジェットエラー対応方法の説明画面
   */
  GadgetErrorSupportWindow = {
    /**
     * showWindow
     */
    showWindow: function () {
      var queries = MyUtil.getUrlQueries();

      // 新しいGoogleサイトで開くURLには「ap=1」をつける
      var newGoogleSiteUrl = window.location.href;
      if (queries['ap'] != '1' && queries['ap'] != 'true') {
        if (newGoogleSiteUrl.indexOf('?') >= 0) {
          newGoogleSiteUrl += '&';
        } else {
          newGoogleSiteUrl += '?';
        }
        newGoogleSiteUrl += 'ap=1';
      }
      newGoogleSiteUrl = newGoogleSiteUrl.replace(/&oidc=cb/g, '');  // コールバック時に付与されるoidc=cbクエリーをカット
      // 別ウインドウで開くURLには「tabmode=1｣をつける(OIDC認証時にprompt=noneをつけないため)
      var gadget_url = window.location.href;
      if (gadget_url.indexOf('?') >= 0) {
        gadget_url += '&';
      } else {
        gadget_url += '?';
      }
      gadget_url += 'tabmode=1';
      gadget_url = gadget_url.replace(/&oidc=cb/g, '');  // コールバック時に付与されるoidc=cbクエリーをカット

      var vHtml = '';
      vHtml += '<div style="margin:10px 10px 30px 10px;font-size:13px;line-height:35px;">';  // start container

      vHtml += Sateraito.Util.escapeHtml(MyLang.getMsg('GADGET_ERROR_SUPPORT_MSG1'));
      vHtml += '<br>';

      // ガジェットエラー対応について
      vHtml += '<p style="font-weight:bold;line-height:20px;margin-top:5px;">' + Sateraito.Util.escapeHtml(MyLang.getMsg('GADGET_ERROR_SUPPORT_WINDOW_TITLE')) + '</p>';
      vHtml += '<div style="margin:5px;font-size:13px;line-height:35px;">';
      vHtml += '<p style="margin:5px;padding:5px;line-height:20px;">';
      vHtml += MyLang.getMsg('GADGET_ERROR_SUPPORT_MSG2');
      vHtml += '<br>';
      vHtml += '<a href="https://sites.sateraito.jp/sateraitooffice/site/manual/home/gsiteerr" target="_blank">' + MyLang.getMsg('GADGET_ERROR_SUPPORT_MSG3') + '</a>';
      vHtml += '</p>';
      vHtml += '<input id="GadgetErrorSupportUrl" type="text" value="' + window.location.href + '"';
      vHtml += ' onclick="this.select(0,this.value.length)"';
      vHtml += ' style="width:550px;font-weight:bold;font-size:12px;padding:5px 10px 5px">';
      vHtml += '<button id="btnGadgetErrorSupportCopy" type="button" style="font-size:12px;">';
      vHtml += MyLang.getMsg('COPY_BUTTON');
      vHtml += '</button>';
      vHtml += '</div>';

      // 新しいGoogleサイトへ移行するためのURL
      vHtml += '<p style="font-weight:bold;line-height:20px;margin-top:25px;">' + Sateraito.Util.escapeHtml(MyLang.getMsg('URL_FOR_NEW_GOOGLE_SITE')) + '</p>';
      vHtml += '<div style="margin:10px;font-size:13px;line-height:35px;">';
      vHtml += '<p style="margin:5px;padding:5px;line-height:20px;">';
      vHtml += Sateraito.Util.escapeHtml(MyLang.getMsg('EXP_URL_FOR_NEW_GOOGLE_SITE'));
      vHtml += '<br>';
      vHtml += '</p>';
      vHtml += '<input id="NewGoogleSiteUrl" type="text" value="' + Sateraito.Util.escapeHtml(newGoogleSiteUrl) + '"';
      vHtml += ' onclick="this.select(0,this.value.length)"';
      vHtml += ' style="width:550px;font-weight:bold;font-size:12px;padding:5px 10px 5px">';
      vHtml += '<button id="btnNewGoogleSiteUrlCopy" type="button" style="font-size:12px;margin-left:5px;">';
      vHtml += Sateraito.Util.escapeHtml(MyLang.getMsg('COPY_BUTTON'));
      vHtml += '</button>';
      vHtml += '</div>';

      vHtml += '</div>';  // end container

      var panel = new Ext.Panel({
        bodyStyle: 'background-color:white;',
        scrollable: true,
        autoWidth: true,
        html: vHtml
      });

      var winGadgetErrorSupportWindow = new Ext.Window({
        width: DisplayMgr.adjustByViewportWidth(750),
        height: DisplayMgr.adjustByViewportHeight(450),
        layout: 'fit',
        plain: true,
        modal: true,
        items: [panel],
        scrollable: true,
        buttons: [],
        listeners: {
          afterrender: function () {
            $('#btnGadgetErrorSupportCopy').on('click', function () {
              MyUtil.setClipboardValue('text/plain', $('#GadgetErrorSupportUrl').val(), function () {
              });
            });
            $('#btnNewGoogleSiteUrlCopy').on('click', function () {
              MyUtil.setClipboardValue('text/plain', $('#NewGoogleSiteUrl').val(), function () {
              });
            });
          }
        },
      });

      winGadgetErrorSupportWindow.show();
    }
  };

  /**
   * カテゴリーノード
   */
  FolderNode = Ext.extend(Ext.tree.TreeNode, {
    constructor: function (config) {
      config = Ext.apply({
        leaf: false,
        expandable: true,
        folderCode: '',
        folderName: '',
        parentFolderCode: '',
        fullPathFolder: '',
        colsToShow: [],
        folder_col_sort: '',
        folder_type_sort: '',
        iconCls: 'mdi mdi-sateraito-folder',
        listeners: {
          expand: function (Node) {
            Node.loadAndAppendChildFolderNode(Node);
          }
        }
      }, config);
      FolderNode.superclass.constructor.call(this, config);
    }
  });

  /**
   * カテゴリー選択ウィンドウ向け文書カテゴリーノード
   * カテゴリーへの権限を考慮する通常ユーザー向け
   */
  FolderNodeForSelectWindow = Ext.extend(FolderNode, {

    /**
     * loadAndAppendChildFolderNode
     *
     * 子カテゴリーをロードし、子ノードとしてアペンドする
     *
     * @param {Object} Node
     */
    loadAndAppendChildFolderNode: function (Node) {
      // 既にアペンド済の場合、アペンドしないで終了
      if (Node.data['appended']) {
        return;
      }
      if (Node.data['is_loading']) {
        return;
      }

      var action = Node.data['action'];
      var folderCode = Node.data['folderCode'];
      var folderColSort = Node.data['folderColSort'];
      var folderTypeSort = Node.data['folderTypeSort'];

      var handlerCallback = function (aJsondata) {
        var folders = aJsondata.folders;
        Ext.each(folders, function () {
          var folderCode = this.folder_code;
          var folderName = this.folder_name;
          var parentFolderCode = this.parent_folder_code;
          var fullPathFolder = this.full_path_folder;
          var folderColSort = this.folder_col_sort;
          var folderTypeSort = this.folder_type_sort;
          var isSubFolderCreatable = this.is_subfolder_creatable;
          var isDeletableFolder = this.is_deletable;

          var newFolderNode = new FolderNodeForSelectWindow({
            text: folderName,
            folderName: folderName,
            folderCode: folderCode,
            parentFolderCode: parentFolderCode,
            fullPathFolder: fullPathFolder,
            folderColSort: folderColSort,
            folderTypeSort: folderTypeSort,
            isSubFolderCreatable: isSubFolderCreatable,
            isDeletableFolder: isDeletableFolder
          });
          Node.appendChild(newFolderNode);
        });

        // アペンド済フラグをオンにする
        Node.data['appended'] = true;

        Node.data['is_loading'] = false;
      }

      Node.data['is_loading'] = true;
      if (MyPanel.nameScreen == 'admin_console') {
        DocFolderRequest.getChildDocFolderByAdmin(folderCode, handlerCallback);
      } else {
        // 自分の子カテゴリーを取得し、ノードとして追加する
        DocFolderRequest.getChildDocFolder(folderCode, action, folderColSort, folderTypeSort, false, handlerCallback);
      }
    }
  });

  /**
   * 数字にカンマを付けたり消したりするユーティリティ
   */
  NumUtil = {

    // (すべての変数に格納する値は0オリジンとする)
    addComma: function (x) { // 引数の例としては 95839285734.3245
      var s = "" + x; // 確実に文字列型に変換する。例では "95839285734.3245"
      var p = s.indexOf("."); // 小数点の位置を0オリジンで求める。例では 11
      if (p < 0) { // 小数点が見つからなかった時
        p = s.length; // 仮想的な小数点の位置とする
      }
      var r = s.substring(p, s.length); // 小数点の桁と小数点より右側の文字列。例では ".3245"
      for (var i = 0; i < p; i++) { // (10 ^ i) の位について
        var c = s.substring(p - 1 - i, p - 1 - i + 1); // (10 ^ i) の位のひとつの桁の数字。例では "4", "3", "7", "5", "8", "2", "9", "3", "8", "5", "9" の順になる。
        if (c < "0" || c > "9") { // 数字以外のもの(符合など)が見つかった
          r = s.substring(0, p - i) + r; // 残りを全部付加する
          break;
        }
        if (i > 0 && i % 3 == 0) { // 3 桁ごと、ただし初回は除く
          r = "," + r; // カンマを付加する
        }
        r = c + r; // 数字を一桁追加する。
      }
      return r; // 例では "95,839,285,734.3245"
    },

    /**
     * removeComma
     *
     * カンマを削除する
     *
     * @param {string} aNumString
     * @return {string}
     */
    removeComma: function (aNumString) {
      if (typeof (aNumString) == 'undefined') {
        return '';
      }
      if (aNumString == null) {
        return '';
      }
      value = '' + aNumString;
      return value.split(',').join('');
    }
  };
})();
