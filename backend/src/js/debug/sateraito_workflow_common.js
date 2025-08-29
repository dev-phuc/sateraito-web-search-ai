/**
 ※本ソースは自動生成されたものです 22/06/2022
 @created: 2022-06-22
 @version: 1.0.0
 @author: Tran Minh Phuc (phuc@vnd.sateraito.co.jp)
 */

(function () {
  /**
   * LocalStrageManager
   *
   */
  LocalStrageManager = {
    get: function (key) {
      if (!Storage) {
        return;
      }

      return localStorage.getItem(key);
    },
    set: function (key, value) {
      if (!Storage) {
        return;
      }

      return localStorage.setItem(key, value);
    },
    remove: function (key) {
      if (!Storage) {
        return;
      }

      return localStorage.removeItem(key);
    },
  };

  /**
   * UserSettingWindow
   *
   */
  UserSettingWindow = {
    window_id: 'user_setting_window',
    /**
     * showWindow
     *
     * チェックカテゴリー設定ウィンドウを表示
     */
    showWindow: function (callback) {
      var self = this;
      // 既に表示されていたら、前面に出す
      var existingWindow = Ext.getCmp(self.window_id);
      if (!(typeof (existingWindow) == 'undefined' || existingWindow == null)) {
        existingWindow.toFront();
        return;
      }

      var buttonCancel = new Ext.Button({
        iconCls: 'mdi mdi-close',
        text: MyLang.getMsg('CANCEL'),
        handler: function () {
          Ext.getCmp(self.window_id).close();
        }
      });

      var buttonSave = new Ext.Button({
        id: 'save_button_' + self.window_id,
        iconCls: 'mdi mdi-content-save',
        text: MyLang.getMsg('SAVE'),
        handler: function (button) {
          button.disable();

          var $form = $('#form_' + self.window_id);
          var new_ui = $form.find(':input[name=\'new_ui\']').is(':checked');
          var new_ui_theme = $form.find(':input[name=\'new_ui_theme\']').val();
          var new_ui_font_size = $form.find(':input[name=\'new_ui_font_size\']').val();
          var new_ui_size = $form.find(':input[name=\'new_ui_size\']').val();
          var new_ui_skin = $form.find(':input[name=\'new_ui_skin\']').val();
          var new_ui_skin_color = $form.find(':input[name=\'new_ui_skin\']').data('color');
          var new_ui_config = {
            active: new_ui_theme,
            themes: {}
          };
          new_ui_config.themes[new_ui_theme] = {
            font_size: new_ui_font_size,
            size: new_ui_size,
            skin: new_ui_skin,
            skin_color: new_ui_skin_color
          };

          var postParams = {
            new_ui: new_ui,
            new_ui_config: JSON.stringify(new_ui_config)
          };
          self.requestUpdateUserSetting(postParams, function (aRetObj) {
            button.enable();
            if (aRetObj.status == 'ok') {
              // 保存に成功した場合
              Ext.Msg.show({
                icon: Ext.MessageBox.INFO,
                msg: MyLang.getMsg('SETTING_SAVED'),
                buttons: Ext.Msg.OK,
                fn: function (buttonId) {
                  Ext.getCmp(self.window_id).close();
                  window.location.reload();
                  return;
                }
              });
            } else {
              Ext.Msg.show({
                icon: Ext.MessageBox.ERROR,
                msg: MyLang.getMsg('ERR_SAVING'),
                buttons: Ext.Msg.OK
              });
            }
          });
        }
      });
      var buttons = [];
      // 保存ボタン
      buttons.push(buttonSave);
      // キャンセルボタン
      buttons.push(buttonCancel);

      var vHtml = '';

      // カテゴリー
      vHtml += '<div id="form_' + self.window_id + '" style="font-size:13px;padding:10px;">';

      vHtml += '<h1>' + MyLang.getMsg('GLOBAL_USER_SETTING') + '</h1>';

      // sateraito new ui 2020-05-07
      vHtml += '<table class="detail jindo">';
      vHtml += '<tr>';
      vHtml += '<td class="detail_name">' + MyLang.getMsg('SATERAITO_NEW_UI') + '</td>';
      vHtml += '<td class="detail_value">';
      vHtml += '<label>';
      vHtml += '<input type="checkbox" name="new_ui">';
      vHtml += '' + MyLang.getMsg('SETTING_SATERAITO_NEW_UI_ACCEPT_FOR_USER_ENABLE');
      vHtml += '</label><br/>';

      vHtml += '        <div class="new_ui_setting_area">';
      vHtml += '          <select style="display:none" name="new_ui_theme"> <option value="material" selected>Material</option> </select>';
      vHtml += '          <div style="margin-top: 7px">';
      vHtml += '            <span>' + MyLang.getMsg('SETTING_SATERAITO_NEW_UI_FONT_SIZE') + '</span>';
      vHtml += '            <input type="number" name="new_ui_font_size" value="13" /><br/>';
      vHtml += '          </div>';
      vHtml += '          <div style="margin-top: 7px">';
      vHtml += '            <span>' + MyLang.getMsg('SETTING_SATERAITO_NEW_UI_SIZE') + '</span>';
      vHtml += '            <select name="new_ui_size">';
      vHtml += '              <option value="small">' + MyLang.getMsg('SETTING_SATERAITO_NEW_UI_SIZE_SMALL') + '</option>'
      vHtml += '              <option value="medium">' + MyLang.getMsg('SETTING_SATERAITO_NEW_UI_SIZE_MEDIUM') + '</option>'
      vHtml += '              <option value="large" selected>' + MyLang.getMsg('SETTING_SATERAITO_NEW_UI_SIZE_LARGE') + '</option>'
      vHtml += '              <option value="x-large">' + MyLang.getMsg('SETTING_SATERAITO_NEW_UI_SIZE_X_LARGE') + '</option>'
      vHtml += '              <option value="xx-large">' + MyLang.getMsg('SETTING_SATERAITO_NEW_UI_SIZE_XX_LARGE') + '</option>'
      vHtml += '            </select>'
      vHtml += '          </div>';
      vHtml += '          <div style="display: inline-block;">';
      vHtml += '            <span>' + MyLang.getMsg('SETTING_SATERAITO_NEW_UI_SKIN') + '</span>';
      vHtml += '            <input type="text" name="new_ui_skin" value="blue" />';
      vHtml += '          </div>';
      vHtml += '        </div>';

      vHtml += '</td>';
      vHtml += '</tr>';
      vHtml += '</table>';

      vHtml += '</div>';

      var settingPanel = {
        xtype: 'panel',
        html: vHtml,
        scrollable: true,
        listeners: {
          afterRender: function () {
            // チェックするカテゴリー設定を取得して表示
            Ext.getCmp('save_button_' + self.window_id).disable();
            var form = $('#form_' + self.window_id);

            self.requestGetUserSetting(function (aSetting) {
              if (aSetting) {
                Ext.getCmp('save_button_' + self.window_id).enable();


                if (aSetting.new_ui) {
                  $(form).find(':input[name=\'new_ui\']').attr('checked', true);
                  $(form).find('.new_ui_setting_area').show();
                } else {
                  $(form).find(':input[name=\'new_ui\']').attr('checked', false);
                  $(form).find('.new_ui_setting_area').hide();
                }
                var skinColors = {
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
                };
                var new_ui_theme = $(form).find(':input[name=\'new_ui_theme\']').val();
                var new_ui_skin = 'blue';
                if (aSetting.new_ui_config) {
                  if (typeof aSetting.new_ui_config.themes[aSetting.new_ui_config.active] != 'undefined') {
                    var theme_config = aSetting.new_ui_config.themes[aSetting.new_ui_config.active];
                    $(form).find(':input[name=\'new_ui_font_size\']').val(theme_config['font_size']);
                    $(form).find(':input[name=\'new_ui_size\']').val(theme_config['size']);
                    $(form).find(':input[name=\'new_ui_skin\']').val(theme_config['skin']);
                    new_ui_skin = theme_config['skin'];
                    skinColors.custom = theme_config['skin_color'] ? theme_config['skin_color'] : '#ffffff';
                  }
                }

                $(form).find(':input[name=\'new_ui_skin\']').SateraitoColorPicker({
                  value: new_ui_skin,
                  buttonSelectText: MyLang.getMsg('SETTING_SATERAITO_NEW_UI_SELECT_SKIN'),
                  skinColors: skinColors,
                  onChange: function (value, color) {
                    $(document.body).attr('skin', value);
                    skinColors.custom = color;
                    var theme = {
                      font_size: $(form).find(':input[name=\'new_ui_font_size\']').val(),
                      skin: value,
                      skin_color: color
                    }
                    var style;
                    if ($('#sateraito_root_css').length) {
                      style = $('#sateraito_root_css')[0];
                    } else {
                      style = document.createElement('style');
                    }
                    var css = ':root,html{font-size: ' + theme.font_size + 'px;}',
                      head = document.head || document.getElementsByTagName('head')[0];
                    if (theme.skin == 'custom') {
                      var color = theme['skin_color'] ? theme['skin_color'] : '#2196f3';
                      css += 'body[skin="custom"]{--base-color: ' + color + ';--base-highlight-color: ' + color + ';--base-light-color: ' + color + ';--base-dark-color: ' + color + ';--base-pressed-color: ' + color + ';--base-focused-color: ' + color + ';}'
                    }
                    if (style.styleSheet) {
                      // This is required for IE8 and below.
                      style.styleSheet.cssText = css;
                    } else {
                      $(style).text('');
                      style.appendChild(document.createTextNode(css));
                    }
                  }
                });

                $(form).find(':input[name=\'new_ui\']').change(function () {
                  if ($(this).is(':checked')) {
                    $(form).find('.new_ui_setting_area').show();
                  } else {
                    $(form).find('.new_ui_setting_area').hide();
                  }
                });

              }
            })
          }
        }
      };

      // サイズ調整
      var windowWidth = 750;
      var windowHeight = 350;
      var viewport = Ext.getCmp('my_viewport');
      if (viewport == null || typeof (viewport) == 'undefined') {
        // no operation
      } else {
        if (viewport.getWidth() < windowWidth) {
          windowWidth = viewport.getWidth();
        }
        if (viewport.getHeight() < windowHeight) {
          windowHeight = viewport.getHeight();
        }
      }

      var title = MyLang.getMsg('SATERAITO_OFFICE_NAME_APP').replace('%1', MyLang.getNameMode());

      // ウィンドウを表示
      var detailWindow = new Ext.Window({
        id: self.window_id,
        width: windowWidth,
        height: windowHeight,
        maximized: false,
        title: title,
        plain: true,
        autoScroll: false,
        layout: 'fit',
        items: [settingPanel],
        modal: true,
        buttons: buttons
      });
      detailWindow.show();
    },

    requestGetUserSetting: function (callback) {
      var baseUrl = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/globalsetting';
      var methodUrl = '/getglobalusersetting';
      SimpleRequest.get({
        baseUrl: baseUrl,
        methodUrl: methodUrl,
        busyMsg: MyLang.getMsg('RELOADING'),
        callback: function (aSetting) {
          callback(aSetting);
        }
      });
    },

    /**
     * requestUpdateUserSetting
     *
     * @param {Array} aPostParams
     * @param {number} aNumRetry
     */
    requestUpdateUserSetting: function (aPostParams, callback, aNumRetry) {
      var baseUrl = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/globalsetting';
      var methodUrl = '/updateglobalusersetting';

      SimpleRequest.post({
        baseUrl: baseUrl,
        methodUrl: methodUrl,
        postData: aPostParams,
        busyMsg: '',
        callback: callback
      });
    }
  };

  /**
   * 全体設定（全てのアプリケーションIDに反映される設定）
   */
  GlobalSettingPanel = {
    /**
     * requestGlobalSetting
     *
     * 全体設定を取得する
     *
     * @param {function} callback
     */
    requestGlobalSetting: function (callback) {
      var baseUrl = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/globalsetting';
      var methodUrl = '/getglobalsetting';

      SimpleRequest.get({
        baseUrl: baseUrl,
        methodUrl: methodUrl,
        callback: callback
      });
    },

    /**
     * requestUpdateGlobalSettingAdmin
     *
     * 全体設定の保存実行
     *
     * @param {object} aPostData
     * @param {callback} callback
     */
    requestUpdateGlobalSettingAdmin: function (aPostData, callback) {
      var baseUrl = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/globalsetting';
      var methodUrl = '/updateglobalsettingadmin';

      SimpleRequest.post({
        baseUrl: baseUrl,
        methodUrl: methodUrl,
        postData: aPostData,
        callback: callback
      });
    }
  };

  /**
   * その他の設定
   */
  OtherSetting = {
    useSateraitoAddressPopup: false,	// 組織アドレス帳連携するかどうか
    sateraitoAddressPopupUrlParam: '',
    enableOtherAppIdReference: false,	// ユーザー情報の他アプリケーションID参照フラグ
    referenceAppId: '',		// 他アプリケーションを参照する場合、そのアプリケーションID
    wordingForFolder: MyLang.getMsg('WORDING_FOR_FOLDER'),

    /**
     * loadWording
     *
     * 文言変更設定をロード
     *
     * @param {function} callback
     */
    loadWording: function (callback) {
      OtherSetting.requestOtherSetting(function (aOtherSetting) {
        // 組織アドレス帳連携
        OtherSetting.useSateraitoAddressPopup = aOtherSetting.use_sateraito_address_popup;
        OtherSetting.sateraitoAddressPopupUrlParam = aOtherSetting.sateraito_address_popup_url_param;
        if (OtherSetting.sateraitoAddressPopupUrlParam == null || typeof (OtherSetting.sateraitoAddressPopupUrlParam) == 'undefined') {
          OtherSetting.sateraitoAddressPopupUrlParam = '';
        }
        // ユーザー情報の他アプリケーションID参照設定
        OtherSetting.enableOtherAppIdReference = aOtherSetting.enable_other_app_id_reference;
        OtherSetting.referenceAppId = aOtherSetting.reference_app_id;
        OtherSetting.colsToShow = Ext.decode(aOtherSetting.cols_to_show);
        OtherSetting.isUserCanDelete = aOtherSetting.is_ok_to_delete_doc;

        // process currency
        OtherSetting.currencyDataRaw = aOtherSetting.currency_data;
        var currencysConvert = [];
        for (var i = 0; i < aOtherSetting.currency_data.length; i++) {
          currencysConvert.push({
            name: aOtherSetting.currency_data[i]
          })
        }
        OtherSetting.currencyData = currencysConvert;

        callback();
      });
    },

    updateImpersonateEmail: function (callback) {
      OtherSetting.requestUpdateImpersonateEmail(function () {
        SateraitoUI.MessageBox({
          title: MyLang.getMsg('SATERAITO_BBS'),
          icon: Ext.MessageBox.INFO,
          msg: MyLang.getMsg('SETTING_SAVED'),
          buttons: Ext.Msg.OK
        });
        if (typeof callback == 'function') {
          callback();
        }
      });
    },

    requestUpdateImpersonateEmail: function (callback) {
      if (IS_OPENID_MODE) {
        OtherSetting._requestUpdateImpersonateEmailOid(callback);
      } else {
        OtherSetting._requestUpdateImpersonateEmail(callback);
      }
    },

    /**
     * _requestUpdateImpersonateEmail
     *
     * @param {Function} callback
     * @param {number} aNumRetry
     */
    _requestUpdateImpersonateEmail: function (callback, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
        // 読込中メッセージを表示
        SateraitoUI.showLoadingMessage();
      }

      var url = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/default/othersetting/updateimpersonateemail';
      gadgets.io.makeRequest(url, function (response) {

        if (!response.data) {

          // response error
          var err = response.errors[0];
          Sateraito.Util.console(err);

          SateraitoUI.showTimerMessage(MyLang.getMsg('RELOADING') + ' ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
            OtherSetting._requestUpdateImpersonateEmail(callback, (aNumRetry + 1));
          } else {
            // エラーメッセージ
            if (response.rc == 401) {
              SateraitoUI.showTimerMessage(MyLang.getMsg('ERROR_TIMEOUT'), 60 * 60 * 24);
            } else {
              SateraitoUI.showTimerMessage(MyLang.getMsg('ERROR_WHILE_LOADING'), 10);
            }
          }

          return;
        }

        // 読込中メッセージを消去
        SateraitoUI.clearMessage();

        var jsondata = response.data;
        // コールバックをキック
        callback(jsondata);
      }, Sateraito.Util.requestParam(true, {}));
    },

    /**
     * _requestUpdateImpersonateEmailOid
     *
     * @param {Function} callback
     * @param {number} aNumRetry
     */
    _requestUpdateImpersonateEmailOid: function (callback, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
        // 読込中メッセージを表示
        SateraitoUI.showLoadingMessage();
      }

      // リクエスト
      Ext.Ajax.request({
        url: SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/default/othersetting/oid/updateimpersonateemail',
        method: 'POST',
        timeout: 1000 * 120,
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
            OtherSetting._requestUpdateImpersonateEmailOid(callback, (aNumRetry + 1));

          } else {
            // １０回リトライしてもだめだった
            // 読込中メッセージを消去
            SateraitoUI.clearMessage();
          }
        }
      });
    },

    /**
     * requestOtherSetting
     *
     * @param {Function} callback
     */
    requestOtherSetting: function (callback) {
      if (IS_OPENID_MODE) {
        OtherSetting._requestOtherSettingOid(callback);
      } else {
        OtherSetting._requestOtherSetting(callback);
      }
    },

    /**
     * _requestOtherSetting
     *
     * @param {Function} callback
     * @param {number} aNumRetry
     */
    _requestOtherSetting: function (callback, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
        // 読込中メッセージを表示
        SateraitoUI.showLoadingMessage();
      }

      var url = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/othersetting/getothersetting';
      gadgets.io.makeRequest(url, function (response) {

        if (!response.data) {

          // response error
          var err = response.errors[0];
          Sateraito.Util.console(err);

          SateraitoUI.showTimerMessage(MyLang.getMsg('RELOADING') + ' ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
            OtherSetting._requestOtherSetting(callback, (aNumRetry + 1));
          } else {
            // エラーメッセージ
            if (response.rc == 401) {
              SateraitoUI.showLoadingMessage(MyLang.getMsg('ERROR_TIMEOUT'));
            } else {
              SateraitoUI.showTimerMessage(MyLang.getMsg('ERROR_WHILE_LOADING'), 10);
            }
          }

          return;
        }

        // 読込中メッセージを消去
        SateraitoUI.clearMessage();

        var jsondata = response.data;
        // コールバックをキック
        callback(jsondata);
      }, Sateraito.Util.requestParam());
    },

    /**
     * _requestOtherSettingOid
     *
     * @param {Function} callback
     * @param {number} aNumRetry
     */
    _requestOtherSettingOid: function (callback, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
        // 読込中メッセージを表示
        SateraitoUI.showLoadingMessage();
      }

      // リクエスト
      Ext.Ajax.request({
        url: SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/othersetting/oid/getothersetting',
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
            OtherSetting._requestOtherSettingOid(callback, (aNumRetry + 1));

          } else {
            // １０回リトライしてもだめだった
            // 読込中メッセージを消去
            SateraitoUI.clearMessage();
          }
        }
      });
    },

    /**
     * requestUpdateOtherSettingAdmin
     *
     * その他の設定を保存
     *
     * @param {object} aSetting
     * @param {Function} callback
     */
    requestUpdateOtherSettingAdmin: function (aSetting, callback) {
      // 更新中メッセージを表示
      SateraitoUI.showLoadingMessage(MyLang.getMsg('UPDATING'));

      var postData = aSetting;

      var baseUrl = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/othersetting';
      var methodUrl = '/updateothersettingadmin';

      SimpleRequest.post({
        baseUrl: baseUrl,
        methodUrl: methodUrl,
        postData: postData,
        callback: function (jsondata) {
          if (jsondata.status == 'error') {
            // コールバックをキック
            callback(false);
          } else {
            // 読込中メッセージを消去
            SateraitoUI.clearMessage();

            // コールバックをキック
            callback(true);
          }
        }
      });
    }
  };

  /**
   * カテゴリー詳細設定ウィンドウ（新規追加・修正用）
   */
  FolderDetailWindow = {
    folderDetail: null,

    /**
     * createSaveButton
     *
     * カテゴリー詳細の保存ボタンを生成
     *
     * @param {string} aFolderCode ... カテゴリーコード
     * @param {function} refreshCallback ... 保存実行後にキックされるコールバック
     * @param {boolean} aIsAdminMode ... アドミンモードで実行するかどうか（アドミンモードで実行する場合、管理者チェックがおこなわれ、管理者の場合権限チェックなしにカテゴリーが保存される）
     * @param {string} aCopyPrivOf ... 権限をコピーする元のカテゴリーコード
     *
     * @return {Object}
     */
    createSaveButton: function (aFolderCode, refreshCallback, aIsAdminMode, aCopyPrivOf) {
      var buttonText = MyLang.getMsg('MSG_UPDATE');
      if (aFolderCode == '__new_folder') {
        buttonText = MyLang.getMsg('MSG_CREATE');
      }

      return {
        xtype: 'button',
        id: 'save_doc_folder_button',
        text: buttonText,
        iconCls: 'mdi mdi-content-save-outline',
        handler: function () {
          FolderDetailWindow.saveFolder(aFolderCode, refreshCallback, aIsAdminMode, aCopyPrivOf);
        }
      };
    },

    /**
     * createDeleteButton
     *
     * カテゴリーの削除ボタンを生成
     *
     * @param {string} aFolderCode .. カテゴリーコード
     * @param {callback} refreshCallback
     */
    createDeleteButton: function (aFolderCode, refreshCallback) {
      return {
        xtype: 'button',
        id: 'delete_folder_button',
        text: MyLang.getMsg('MSG_DELETE'),
        iconCls: 'mdi mdi-trash-can-outline',
        handler: function () {
          Ext.Msg.show({
            icon: Ext.MessageBox.QUESTION,
            msg: MyLang.getMsg('CONFIRM_DELETE_SOMETHING').replace('%1', OtherSetting.wordingForFolder),
            buttons: Ext.Msg.OKCANCEL,
            fn: function (buttonId) {
              if (buttonId == 'ok') {

                // 削除実行
                var adminMode = true;
                Ext.getCmp('window_doc_folder').setLoading(true);
                DocFolderManager.delete([aFolderCode], function (success, errorCode) {
                  Ext.getCmp('window_doc_folder').setLoading(false);
                  if (success) {
                    Ext.defer(function () {
                      // カテゴリーツリーの再描画
                      refreshCallback(Constants.TASK_AFTER_DELETED, [aFolderCode]);
                      Ext.getCmp('window_doc_folder').close();
                    }, 500);
                  } else {
                    SateraitoUI.MessageBox({
                      icon: Ext.MessageBox.ERROR,
                      msg: MyLang.getMsgByCode(errorCode, MyLang.getMsg('MSG_DELETE_FAILED')),
                      buttons: Ext.Msg.OK,
                      fn: function (buttonId) {
                      }
                    });
                  }
                }, adminMode);
              }
            }
          });
        }
      };
    },

    /**
     * createCopyButton
     *
     * @param {string} aFolderCode
     * @param {callback} refreshCallback
     */
    createCopyButton: function (aFolderCode, refreshCallback) {
      return {
        xtype: 'button',
        id: 'copy_folder_button',
        text: MyLang.getMsg('MSG_COPY'),
        iconCls: 'mdi mdi-folder-multiple-outline',
        handler: function () {
          var onSelectFolder = function (folderCode, folderName) {
            if (folderCode != '') {
              SateraitoUI.MessageBox({
                icon: Ext.MessageBox.QUESTION,
                msg: MyLang.getMsg('TXT_CONFIRM_COPY_FOLDER_TO_FOLDER_SELECTED'),
                buttons: Ext.Msg.OKCANCEL,
                fn: function (res) {
                  if (res == 'ok') {
                    Ext.getCmp('window_doc_folder').setLoading(true);
                    DocFolderManager.copy([aFolderCode], folderCode, function (success, errorCode) {
                      Ext.getCmp('window_doc_folder').setLoading(false);
                      if (success) {
                        Ext.defer(function () {
                          // カテゴリーツリーの再描画
                          if (typeof (refreshCallback) == 'function') {
                            refreshCallback(Constants.TASK_AFTER_COPY, FolderDetailWindow.folderDetail, errorCode);
                          }

                          Ext.getCmp('window_doc_folder').close();
                        }, 500);
                      } else {
                        SateraitoUI.MessageBox({
                          icon: Ext.MessageBox.ERROR,
                          msg: MyLang.getMsgByCode(errorCode, MyLang.getMsg('MSG_ERROR_COPY_FOLDER')),
                          buttons: Ext.Msg.OK,
                          fn: function (buttonId) {
                          }
                        });
                      }

                    }, true);
                  }
                }
              });
            }
          }

          // Select folder move to
          var title = MyLang.getMsg('SELECT_COPY_SOMETHING').replaceAll('%1', OtherSetting.wordingForFolder)
          FolderSelectedWindow.showWindow(onSelectFolder, true, title);
        }
      };
    },

    /**
     * createMoveButton
     *
     * @param {string} aFolderCode
     * @param {callback} refreshCallback
     */
    createMoveButton: function (aFolderCode, refreshCallback) {
      return {
        xtype: 'button',
        id: 'move_folder_button',
        text: MyLang.getMsg('MSG_MOVE'),
        iconCls: 'mdi mdi-folder-move',
        handler: function () {
          var onSelectFolder = function (folderCode, folderName) {
            if (folderCode != '') {
              SateraitoUI.MessageBox({
                icon: Ext.MessageBox.QUESTION,
                msg: MyLang.getMsg('TXT_CONFIRM_MOVE_FOLDER_TO_FOLDER_SELECTED'),
                buttons: Ext.Msg.OKCANCEL,
                fn: function (res) {
                  if (res == 'ok') {
                    Ext.getCmp('window_doc_folder').setLoading(true);
                    DocFolderManager.move([aFolderCode], folderCode, function (success, errorCode) {
                      Ext.getCmp('window_doc_folder').setLoading(false);
                      if (success) {
                        Ext.defer(function () {
                          // カテゴリーツリーの再描画
                          if (typeof(refreshCallback) == 'function') {
                            refreshCallback(Constants.TASK_AFTER_MOVE, FolderDetailWindow.folderDetail, errorCode);
                          }

                          Ext.getCmp('window_doc_folder').close();
                        }, 500);
                      } else {
                        SateraitoUI.MessageBox({
                          icon: Ext.MessageBox.ERROR,
                          msg: MyLang.getMsgByCode(errorCode, MyLang.getMsg('MSG_ERROR_MOVE_FOLDER')),
                          buttons: Ext.Msg.OK,
                          fn: function (buttonId) {
                          }
                        });
                      }

                    }, true);
                  }
                }
              });
            }
          };

          // Select folder move to
          var title = MyLang.getMsg('SELECT_MOVE_SOMETHING').replaceAll('%1', OtherSetting.wordingForFolder)
          FolderSelectedWindow.showWindow(onSelectFolder, true, title);
        }
      };
    },

    /**
     * enableDeletableInputsByCheck
     *
     * 「管理画面でのみ削除可能」がチェックされた場合、削除可能なユーザー、削除可能や役職、削除可能な部署1を入力不可にする
     * チェックされていない場合、入力可能とする
     */
    enableDeletableInputsByCheck: function () {
      if ($('#folder_detail_form').find(':input[name=\'deletable_admin_only\']').is(':checked')) {

        // 「管理画面でのみ削除可能」がチェックされている場合、入力項目をdisableする

        $('#folder_detail_form').find(':input[name=\'deletable_users\']').attr('disabled', 'disabled');
      } else {
        // 「管理画面でのみ削除可能」がチェックされていない場合、入力項目をenableする
        $('#folder_detail_form').find(':input[name=\'deletable_users\']').removeAttr('disabled');
      }
    },

    /**
     * enableSubfolderCreatableInputsByCheck
     *
     * 「一般ユーザーの下位カテゴリー作成・削除を禁止」がチェックされていない場合だけ、ユーザー／グループアドレスが入力できるよう、
     * 入力ボックスをEnable/Disableする
     */
    enableSubfolderCreatableInputsByCheck: function () {
      if ($('#folder_detail_form').find(':input[name=\'subfolder_creatable_admin_only\']').is(':checked')) {

        // 「一般ユーザーの下位カテゴリー作成・削除を禁止」がチェックされている場合、入力項目をdisableする

        $('#folder_detail_form').find(':input[name=\'subfolder_creatable_users\']').attr('disabled', 'disabled');
      } else {
        // 「一般ユーザーの下位カテゴリー作成・削除を禁止」がチェックされていない場合、入力項目をenableする
        $('#folder_detail_form').find(':input[name=\'subfolder_creatable_users\']').removeAttr('disabled');
      }
    },

    /**
     * enableCreatableInputsByCheck
     *
     * 「一覧表示権限と同じ」がチェックされた場合、新規作成可能なユーザー、新規作成可能や役職、新規作成可能な部署1を入力不可にする
     * チェックされていない場合、入力可能とする
     */
    enableCreatableInputsByCheck: function () {
      if ($('#folder_detail_form').find(':input[name=\'creatable_same_accessible\']').is(':checked')) {

        // 「一覧表示権限と同じ」がチェックされている場合、入力項目をdisableする

        $('#folder_detail_form').find(':input[name=\'creatable_users\']').attr('disabled', 'disabled');
      } else {
        // 「一覧表示権限と同じ」がチェックされていない場合、入力項目をenableする
        $('#folder_detail_form').find(':input[name=\'creatable_users\']').removeAttr('disabled');
      }
    },

    /**
     * enableDownloadableInputsByCheck
     *
     * （ダウンロード権限）「一覧表示権限と同じ」がチェックされた場合、新規作成可能なユーザー、新規作成可能や役職、新規作成可能な部署1を入力不可にする
     * チェックされていない場合、入力可能とする
     */
    enableDownloadableInputsByCheck: function () {
      if ($('#folder_detail_form').find(':input[name=\'downloadable_same_accessible\']').is(':checked')) {

        // 「一覧表示権限と同じ」がチェックされている場合、入力項目をdisableする

        $('#folder_detail_form').find(':input[name=\'downloadable_users\']').attr('disabled', 'disabled');
      } else {
        // 「一覧表示権限と同じ」がチェックされていない場合、入力項目をenableする
        $('#folder_detail_form').find(':input[name=\'downloadable_users\']').removeAttr('disabled');
      }
    },

    /**
     * enableButtons
     *
     * ウィンドウの下側に表示されている３つのボタンをenable/disableする
     *
     * @param {boolean} aEnable
     */
    enableButtons: function (aEnable) {
      if (typeof (aEnable) == 'undefined') {
        aEnable = true;
      }
      var buttons = ['save_doc_folder_button', 'close_folder_window', 'delete_folder_button', 'copy_folder_button', 'move_folder_button'];
      Ext.each(buttons, function () {
        var btn = Ext.getCmp('' + this);
        if (btn) {
          if (aEnable) {
            btn.enable();
          } else {
            btn.disable();
          }
        }
      });
    },

    /**
     * disableButtons
     *
     * ウィンドウの下側に表示されている３つのボタンをdisableする
     */
    disableButtons: function () {
      FolderDetailWindow.enableButtons(false);
    },

    /**
     * privTabHtmlViewable
     *
     * 「一覧表示権限」タブに表示するhtml
     *
     * @return {string}
     */
    privTabHtmlViewable: function () {
      var vHtml = '';

      vHtml += '<div>';
      vHtml += '<table class="detail jindo">';

      vHtml += '<tr>';
      vHtml += '<td class="detail_name">';
      vHtml += MyLang.getMsg('ACCESS_PERMITTED_USER_GROUP');
      vHtml += '<td>';
      vHtml += '<td class="detail_value">';
      vHtml += '<input type="text" name="accessible_users" style="width:100%">';
      vHtml += '<br /><span class="description">';
      vHtml += MyLang.getMsg('EXP_ACCESS_PERMITTED_USER_GROUP_CATEGORY').replace(/%1/g, OtherSetting.wordingForFolder);
      vHtml += '</span>';

      // 組織アドレス帳連携
      vHtml += '<input type="hidden" id="address_string_accessible_users">';		// 組織アドレス帳から取得した値を一時保管する領域
      vHtml += '<input type="button" name="sateraito_address_search_send_mail" value="' + MyLang.getMsg('ADD_FROM_ADDRESS_BOOK') + '"';
      if (OtherSetting.useSateraitoAddressPopup) {
        // 組織アドレス帳と連携する場合
        // no operation
      } else {
        // 組織アドレス帳と連携しない場合、ボタンは非表示とする
        vHtml += ' style="display:none;"';
      }
      vHtml += ' onclick="';
      vHtml += '$(\'#address_string_accessible_users\').val(\'\');';
      vHtml += 'KozukasanPopup.sateraitoShowPopup2(\'address_string_accessible_users\', function(){';
      vHtml += 'MyPanel.convertAddressStr(\'address_string_accessible_users\', \'folder_detail_form\', \'accessible_users\');';
      vHtml += '});">';

      vHtml += '<td>';
      vHtml += '</tr>';

      vHtml += '</table>';
      vHtml += '</div>';

      return vHtml;
    },

    /**
     * privTabHtmlCreatable
     *
     * 「ファイルアップロード権限」タブに表示するhtml
     *
     * @return {string}
     */
    privTabHtmlCreatable: function () {
      var vHtml = '';

      vHtml += '<div>';
      vHtml += '<table class="detail jindo">';

      vHtml += '<tr>';
      vHtml += '<td class="detail_name">';
      vHtml += MyLang.getMsg('SAME_AS_ACCESS_PERMISSION');
      vHtml += '<td>';
      vHtml += '<td class="detail_value">';
      vHtml += '<input type="checkbox" name="creatable_same_accessible" id="creatable_same_accessible"><label for="creatable_same_accessible">';
      vHtml += MyLang.getMsg('SAME_AS_ACCESS_PERMISSION');
      vHtml += '</label>';
      vHtml += '<br /><span class="description">';
      vHtml += MyLang.getMsg('EXP_SAME_AS_ACCESSIBLE_CREATABLE').replace(/%1/g, OtherSetting.wordingForFolder);
      vHtml += '</span>';
      vHtml += '<td>';
      vHtml += '</tr>';

      vHtml += '<tr>';
      vHtml += '<td class="detail_name">';
      vHtml += MyLang.getMsg('CREATE_PERMITTED_USER_GROUP');
      vHtml += '<td>';
      vHtml += '<td class="detail_value">';
      vHtml += '<input type="text" name="creatable_users" style="width:100%">';
      vHtml += '<br /><span class="description">';
      vHtml += MyLang.getMsg('EXP_CREATE_PERMITTED_USER_GROUP_CATEGORY').replace(/%1/g, OtherSetting.wordingForFolder);
      vHtml += '</span>';

      // 組織アドレス帳連携
      vHtml += '<input type="hidden" id="address_string_creatable_users">';		// 組織アドレス帳から取得した値を一時保管する領域
      vHtml += '<input type="button" name="sateraito_address_search_send_mail" value="' + MyLang.getMsg('ADD_FROM_ADDRESS_BOOK') + '"';
      if (OtherSetting.useSateraitoAddressPopup) {
        // 組織アドレス帳と連携する場合
        // no operation
      } else {
        // 組織アドレス帳と連携しない場合、ボタンは非表示とする
        vHtml += ' style="display:none;"';
      }
      vHtml += ' onclick="';
      vHtml += '$(\'#address_string_creatable_users\').val(\'\');';
      vHtml += 'KozukasanPopup.sateraitoShowPopup2(\'address_string_creatable_users\', function(){';
      vHtml += 'MyPanel.convertAddressStr(\'address_string_creatable_users\', \'folder_detail_form\', \'creatable_users\');';
      vHtml += '});">';

      vHtml += '<td>';
      vHtml += '</tr>';

      vHtml += '</table>';
      vHtml += '</div>';

      return vHtml;
    },

    /**
     * privTabHtmlDownloadable
     *
     * ダウンロード権限タブの内容のhtmlを返す
     *
     * @return {string}
     */
    privTabHtmlDownloadable: function () {
      var vHtml = '';

      vHtml += '<div>';
      vHtml += '<table class="detail jindo">';

      vHtml += '<tr>';
      vHtml += '<td class="detail_name">';
      vHtml += MyLang.getMsg('SAME_AS_ACCESS_PERMISSION');
      vHtml += '<td>';
      vHtml += '<td class="detail_value">';
      vHtml += '<input type="checkbox" name="downloadable_same_accessible" id="downloadable_same_accessible"><label for="downloadable_same_accessible">';
      vHtml += MyLang.getMsg('SAME_AS_ACCESS_PERMISSION');
      vHtml += '</label>';
      vHtml += '<br /><span class="description">';
      vHtml += MyLang.getMsg('DOWNLOAD_SAME_AS_ACCESS_PERMISSION').replace(/%1/g, OtherSetting.wordingForFolder);
      vHtml += '</span>';
      vHtml += '<td>';
      vHtml += '</tr>';

      vHtml += '<tr>';
      vHtml += '<td class="detail_name">';
      vHtml += MyLang.getMsg('DOWNLOAD_PERMITTED_USER_GROUP');
      vHtml += '<td>';
      vHtml += '<td class="detail_value">';
      vHtml += '<input type="text" name="downloadable_users" style="width:100%">';
      vHtml += '<br /><span class="description">';
      vHtml += MyLang.getMsg('EXP_DOWNLOAD_PERMITTED_USER_GROUP_CATEGORY').replace(/%1/g, OtherSetting.wordingForFolder);
      vHtml += '</span>';

      // 組織アドレス帳連携
      vHtml += '<input type="hidden" id="address_string_downloadable_users">';		// 組織アドレス帳から取得した値を一時保管する領域
      vHtml += '<input type="button" name="sateraito_address_search_send_mail" value="' + MyLang.getMsg('ADD_FROM_ADDRESS_BOOK') + '"';
      if (OtherSetting.useSateraitoAddressPopup) {
        // 組織アドレス帳と連携する場合
        // no operation
      } else {
        // 組織アドレス帳と連携しない場合、ボタンは非表示とする
        vHtml += ' style="display:none;"';
      }
      vHtml += ' onclick="';
      vHtml += '$(\'#address_string_downloadable_users\').val(\'\');';
      vHtml += 'KozukasanPopup.sateraitoShowPopup2(\'address_string_downloadable_users\', function(){';
      vHtml += 'MyPanel.convertAddressStr(\'address_string_downloadable_users\', \'folder_detail_form\', \'downloadable_users\');';
      vHtml += '});">';

      vHtml += '<td>';
      vHtml += '</tr>';

      vHtml += '</table>';
      vHtml += '</div>';

      return vHtml;
    },

    /**
     * privTabHtmlDeletable
     *
     * 削除権限タブのhtmlを返す
     *
     * @return {string}
     */
    privTabHtmlDeletable: function () {
      var vHtml = '';

      vHtml += '<div>';
      vHtml += '<table class="detail jindo">';

      vHtml += '<tr>';
      vHtml += '<td class="detail_name">';
      vHtml += MyLang.getMsg('DELETABLE_ONLY_IN_ADMIN_CONSOLE');
      vHtml += '<td>';
      vHtml += '<td class="detail_value">';
      vHtml += '<input type="checkbox" name="deletable_admin_only" id="deletable_admin_only"><label for="deletable_admin_only">';
      vHtml += MyLang.getMsg('DELETABLE_ONLY_IN_ADMIN_CONSOLE');
      vHtml += '</label>';
      vHtml += '<br /><span class="description">';
      vHtml += MyLang.getMsg('EXP_DELETABLE_ONLY_IN_ADMIN_CONSOLE').replace(/%1/g, OtherSetting.wordingForFolder);
      vHtml += '</span>';
      vHtml += '<td>';
      vHtml += '</tr>';

      vHtml += '<tr>';
      vHtml += '<td class="detail_name">';
      vHtml += MyLang.getMsg('DELETE_PERMITTED_USER_GROUP');
      vHtml += '<td>';
      vHtml += '<td class="detail_value">';
      vHtml += '<input type="text" name="deletable_users" style="width:100%">';
      vHtml += '<br /><span class="description">';
      vHtml += MyLang.getMsg('EXP_DELETE_PERMITTED_USER_GROUP_CATEGORY').replace(/%1/g, OtherSetting.wordingForFolder);
      vHtml += '</span>';

      // 組織アドレス帳連携
      vHtml += '<input type="hidden" id="address_string_deletable_users">';		// 組織アドレス帳から取得した値を一時保管する領域
      vHtml += '<input type="button" name="sateraito_address_search_send_mail" value="' + MyLang.getMsg('ADD_FROM_ADDRESS_BOOK') + '"';
      if (OtherSetting.useSateraitoAddressPopup) {
        // 組織アドレス帳と連携する場合
        // no operation
      } else {
        // 組織アドレス帳と連携しない場合、ボタンは非表示とする
        vHtml += ' style="display:none;"';
      }
      vHtml += ' onclick="';
      vHtml += '$(\'#address_string_deletable_users\').val(\'\');';
      vHtml += 'KozukasanPopup.sateraitoShowPopup2(\'address_string_deletable_users\', function(){';
      vHtml += 'MyPanel.convertAddressStr(\'address_string_deletable_users\', \'folder_detail_form\', \'deletable_users\');';
      vHtml += '});">';

      vHtml += '<td>';
      vHtml += '</tr>';

      vHtml += '</table>';
      vHtml += '</div>';

      return vHtml;
    },

    /**
     * privTabHtmlSubFolderCreatable
     *
     * サブカテゴリー作成／削除権限タブのhtmlを返す
     *
     * @return {string}
     */
    privTabHtmlSubFolderCreatable: function () {
      var vHtml = '';

      vHtml += '<div>';
      vHtml += '<table class="detail jindo">';

      vHtml += '<tr>';
      vHtml += '<td class="detail_name">';
      vHtml += MyLang.getMsg('SUBCATEGORY_ONLY_IN_ADMIN_CONSOLE').replace(/%1/g, OtherSetting.wordingForFolder);
      vHtml += '<td>';
      // 一般ユーザーの下位カテゴリー作成・削除を禁止
      vHtml += '<td class="detail_value">';
      vHtml += '<input type="checkbox" name="subfolder_creatable_admin_only" id="subfolder_creatable_admin_only"><label for="subfolder_creatable_admin_only">';
      vHtml += MyLang.getMsg('SUBCATEGORY_ONLY_IN_ADMIN_CONSOLE').replace(/%1/g, OtherSetting.wordingForFolder);
      vHtml += '</label>';
      vHtml += '<br /><span class="description">';
      vHtml += MyLang.getMsg('EXP_SUBCATEGORY_ONLY_IN_ADMIN_CONSOLE').replace(/%1/g, OtherSetting.wordingForFolder);
      vHtml += '</span>';
      vHtml += '<td>';
      vHtml += '</tr>';

      vHtml += '<tr>';
      vHtml += '<td class="detail_name" nowrap>';
      vHtml += MyLang.getMsg('SUBCATEGORY_PERMITTED_USER_GROUP').replace(/%1/g, OtherSetting.wordingForFolder);
      vHtml += '<td>';
      // 下位カテゴリー作成・削除可能なユーザー／グループ
      vHtml += '<td class="detail_value">';
      vHtml += '<input type="text" name="subfolder_creatable_users" style="width:100%">';
      vHtml += '<br /><span class="description">';
      vHtml += MyLang.getMsg('EXP_SUBCATEGORY_PERMITTED_USER_GROUP_CATEGORY').replace(/%1/g, OtherSetting.wordingForFolder);
      vHtml += '</span>';

      // 組織アドレス帳連携
      vHtml += '<input type="hidden" id="address_string_subfolder_creatable_users">';		// 組織アドレス帳から取得した値を一時保管する領域
      vHtml += '<input type="button" name="sateraito_address_search_send_mail" value="' + MyLang.getMsg('ADD_FROM_ADDRESS_BOOK') + '"';
      if (OtherSetting.useSateraitoAddressPopup) {
        // 組織アドレス帳と連携する場合
        // no operation
      } else {
        // 組織アドレス帳と連携しない場合、ボタンは非表示とする
        vHtml += ' style="display:none;"';
      }
      vHtml += ' onclick="';
      vHtml += '$(\'#address_string_subfolder_creatable_users\').val(\'\');';
      vHtml += 'KozukasanPopup.sateraitoShowPopup2(\'address_string_subfolder_creatable_users\', function(){';
      vHtml += 'MyPanel.convertAddressStr(\'address_string_subfolder_creatable_users\', \'folder_detail_form\', \'subfolder_creatable_users\');';
      vHtml += '});">';

      vHtml += '<td>';
      vHtml += '</tr>';

      vHtml += '</table>';
      vHtml += '</div>';

      return vHtml;
    },

    /**
     * renderPrivSettingPanel
     *
     * 権限設定パネルを描画する
     */
    renderPrivSettingPanel: function () {
      // タブを構築・描画
      var tabPanel = {
        xtype: 'tabpanel',
        activeTab: 0,
        enableTabScroll: true,
        plain: true,
        frame: true,
        bodyStyle: 'background-color:white;',
        region: 'center',
        items: [{
          title: MyLang.getMsg('ACCESS_PERMISSION'),
          scrollable: true,
          html: FolderDetailWindow.privTabHtmlViewable()
        }, {
          title: MyLang.getMsg('UPLOAD_PERMISSION'),
          scrollable: true,
          html: FolderDetailWindow.privTabHtmlCreatable()
        }, {
          title: MyLang.getMsg('DOWNLOAD_PERMISSION'),
          scrollable: true,
          html: FolderDetailWindow.privTabHtmlDownloadable()
        }, {
          title: MyLang.getMsg('DELETE_PERMISSION'),
          scrollable: true,
          html: FolderDetailWindow.privTabHtmlDeletable()
        }, {
          title: MyLang.getMsg('SUBCATEGORY_CREATABLE_PERMISSION').replace(/%1/g, OtherSetting.wordingForFolder),
          scrollable: true,
          html: FolderDetailWindow.privTabHtmlSubFolderCreatable()
        }],
        listeners: {
          afterrender: function (tabPanel) {
            for (let i = 0; i < tabPanel.items.items.length; i++) {
              tabPanel.setActiveTab(i)
            }
            tabPanel.setActiveTab(0)
          }
        }
      };

      var vHtml = '<div style="margin:10px 5px; padding:5px;">';
      vHtml += MyLang.getMsg('MAIL_ADDRESS_TO_NOTIFY_ON_NEW_FILE') + ': ';
      vHtml += '<input type="text" name="notice_mails" style="width:100%">';
      vHtml += '<p class="description">';
      vHtml += MyLang.getMsg('EXP_MAIL_ADDRESS_TO_NOTIFY_ON_NEW_FILE').replace(/%1/g, OtherSetting.wordingForFolder);
      vHtml += '</p>';
      vHtml += '</div>';

      ExtMixins.destroyById('priv_setting_tab_panel');
      var parentPanel = {
        xtype: 'panel',
        id: 'priv_setting_tab_panel',
        renderTo: 'priv_setting_panel_render_area',
        title: MyLang.getMsg('AUTHORITY_SETTING'),  // 権限設定
        width: 'auto',
        height: 400,
        border: false,
        plain: true,
        bodyStyle: 'background-color:white;',
        layout: 'border',
        items: [
          tabPanel,
          {
            // height: 100,
            border: false,
            region: 'south',
            html: vHtml
          }
        ]
      };

      return Ext.create(parentPanel);
    },

    /**
     * saveFolder
     *
     * カテゴリーの保存実行
     *
     * @param {string} aFolderCode
     * @param {function} refreshCallback
     * @param {boolean} aIsAdminMode
     * @param {string} aCopyPrivOf
     */
    saveFolder: function (aFolderCode, refreshCallback, aIsAdminMode, aCopyPrivOf) {
      var insertFlag = '0';
      if (aFolderCode == '__new_folder') {
        insertFlag = '1';
      }
      var folderCode = $('#folder_detail_form').find(':input[name=\'folder_code\']').val();
      var folderName = $('#folder_detail_form').find(':input[name=\'folder_name\']').val();
      // 一覧表示権限
      var accessibleUsers = $('#folder_detail_form').find(':input[name=\'accessible_users\']').val();
      // ファイルアップロード権限
      var creatableSameAccessible = $('#folder_detail_form').find(':input[name=\'creatable_same_accessible\']').is(':checked');
      var creatableUsers = $('#folder_detail_form').find(':input[name=\'creatable_users\']').val();
      // ダウンロード権限
      var downloadableSameAccessible = $('#folder_detail_form').find(':input[name=\'downloadable_same_accessible\']').is(':checked');
      var downloadableUsers = $('#folder_detail_form').find(':input[name=\'downloadable_users\']').val();
      // 削除権限
      var deletableAdminOnly = $('#folder_detail_form').find(':input[name=\'deletable_admin_only\']').is(':checked');
      var deletableUsers = $('#folder_detail_form').find(':input[name=\'deletable_users\']').val();
      // 下位カテゴリー作成・削除権限
      var subfolderCreatableAdminOnly = $('#folder_detail_form').find(':input[name=\'subfolder_creatable_admin_only\']').is(':checked');
      var subfolderCreatableUsers = $('#folder_detail_form').find(':input[name=\'subfolder_creatable_users\']').val();

      // カテゴリー名称チェック
      folderName = folderName.trim();
      if (folderName == '') {
        // カテゴリー名を入力して下さい
        Ext.Msg.show({
          icon: Ext.MessageBox.ERROR,
          msg: MyLang.getMsg('ENTER_SOMETHING_NAME').replace(/%1/g, OtherSetting.wordingForFolder),
          buttons: Ext.Msg.OK,
          fn: function (buttonId) {
            $('#folder_detail_form').find(':input[name=\'folder_name\']')[0].focus();
          }
        });
        return;
      }

      // 親カテゴリーコード
      var parentFolderCode = $('#folder_detail_form').find(':input[name=\'parent_folder_code\']').val();

      var folderColSort = Ext.getCmp('folder_col_sort').getValue();
      var folderTypeSort = Ext.getCmp('folder_type_sort').getValue();

      // 通知先メールアドレス
      var noticeMails = ('' + $('#folder_detail_form').find(':input[name=\'notice_mails\']').val()).trim();

      // メール通知URLをチェック
      if (noticeMails != '') {
        if (!Sateraito.Util.isAllSplitedValEmail(noticeMails)) {
          Ext.Msg.show({
            icon: Ext.MessageBox.INFO,
            msg: MyLang.getMsg('SETTING_HAVE_NON_EMAIL_FORMAT_STRING'),
            buttons: Ext.Msg.OK,
            fn: function (buttonId) {
              $('#folder_detail_form').find(':input[name=\'notice_mails\']')[0].focus();
            }
          });
          return;
        }
      }
      // }

      // ボタンをいったんDisable
      FolderDetailWindow.disableButtons();

      var postData = {
        screen: LoginMgr.screenName,
        insert_flag: insertFlag,
        folder_code: folderCode,
        folder_name: folderName,
        parent_folder_code: parentFolderCode,

        folder_col_sort: folderColSort,
        folder_type_sort: folderTypeSort,

        notice_mails: noticeMails,

        accessible_users: accessibleUsers,

        creatable_same_accessible: creatableSameAccessible,
        creatable_users: creatableUsers,

        downloadable_same_accessible: downloadableSameAccessible,
        downloadable_users: downloadableUsers,

        deletable_admin_only: deletableAdminOnly,
        deletable_users: deletableUsers,

        subfolder_creatable_admin_only: subfolderCreatableAdminOnly,
        subfolder_creatable_users: subfolderCreatableUsers,

        copy_priv_of: aCopyPrivOf,

        lang: MyLang.getLocale()
      };

      FolderDetailWindow._saveFolder(postData, refreshCallback, aIsAdminMode);
    },

    /**
     * _saveFolder
     *
     * カテゴリー設定の保存実行
     *
     * @param {object} postData
     * @param refreshCallback
     * @param aIsAdminMode
     */
    _saveFolder: function (postData, refreshCallback, aIsAdminMode) {
      Ext.getCmp('window_doc_folder').setLoading(true);

      // 新規またはアップデート実行
      DocFolderManager.update(postData, function (success, dataFolder, errorCode) {

        // ボタンをEnable
        FolderDetailWindow.enableButtons();

        if (success) {
          Ext.defer(function () {
            // カテゴリーツリーを再構築
            if (postData.insert_flag == '1') {
              refreshCallback(Constants.TASK_AFTER_CREATED, dataFolder);
            } else {
              refreshCallback(Constants.TASK_AFTER_UPDATED, dataFolder);
            }

            // ウィンドウを閉じる
            Ext.getCmp('window_doc_folder').close();
          }, 500)
        } else {
          SateraitoUI.MessageBox({
            icon: Ext.MessageBox.ERROR,
            msg: MyLang.getMsgByCode(errorCode, MyLang.getMsg('MSG_UPDATE_FAILED')),
            buttons: Ext.Msg.OK,
            fn: function (buttonId) {
            }
          });
        }
      }, aIsAdminMode);
    },

    /**
     * setPanelEnabled
     *
     * カテゴリーの種類によって設定パネルのEnable/Disableを設定する
     */
    setPanelEnabled: function () {
      var form = $('#folder_detail_form');
      // 権限設定パネル
      Ext.getCmp('priv_setting_tab_panel').enable();
      Ext.getCmp('folder_col_sort').enable();
      Ext.getCmp('folder_type_sort').enable();
    },

    /**
     * showWindow
     *
     * カテゴリー追加／変更ウィンドウを表示
     *
     * @param {string} aFolderCode ... カテゴリーコード、"__new_folder"の場合新規カテゴリー追加ウィンドウを表示
     * @param {string} aParentFolderCode .. 親カテゴリーコード、"__root"の場合ルート下にカテゴリーを追加
     *                                        新規カテゴリー追加の時だけ使われる（既存カテゴリー表示の場合このパラメータは使われない）
     * @param refreshCallback
     * @param aIsAdminMode
     * @param aCopyPrivOf
     */
    showWindow: function (aFolderCode, aParentFolderCode, refreshCallback, aIsAdminMode, aCopyPrivOf) {
      // カテゴリー追加ウィンドウが表示されていたら、前面に出す
      var existingWindow = Ext.getCmp('window_doc_folder');
      if (!(typeof (existingWindow) == 'undefined' || existingWindow == null)) {
        existingWindow.toFront();
        return;
      }

      if (typeof (aParentFolderCode) == 'undefined') {
        aParentFolderCode = Constants.ROOT_FOLDER_CODE;
      }
      if (typeof (aCopyPrivOf) == 'undefined') {
        aCopyPrivOf = '';
      }

      var title = MyLang.getMsg('SOMETHING_DETAIL').replace('%1', OtherSetting.wordingForFolder);
      if (aFolderCode == '__new_folder') {
        title = MyLang.getMsg('ADD_SOMETHING').replace('%1', OtherSetting.wordingForFolder);
      }

      // カテゴリー詳細画面html
      var vHtml = '';
      vHtml += '<div>';
      vHtml += '<form id="folder_detail_form">';
      vHtml += '<table class="detail jindo">';

      //
      // カテゴリーコードは表示しない（新規追加の場合は、自動採番）
      //
      vHtml += '<input type="hidden" name="folder_code">';

      // カテゴリー名
      vHtml += '<tr>';
      vHtml += '<td class="detail_name">';
      vHtml += MyLang.getMsg('SOMETHING_NAME').replace(/%1/g, OtherSetting.wordingForFolder);
      vHtml += '<td>';
      vHtml += '<td class="detail_value">';
      vHtml += '<input type="text" name="folder_name" maxlength="100" style="width:100%">';
      vHtml += '<br /><span class="description">';
      vHtml += MyLang.getMsg('EXP_CATEGORY_NAME');
      vHtml += '</span>';
      vHtml += '</td>';
      vHtml += '</tr>';
      // 親カテゴリー
      vHtml += '<tr>';
      vHtml += '<td class="detail_name">';
      vHtml += MyLang.getMsg('PARENT_SOMETHING').replace(/%1/g, OtherSetting.wordingForFolder);
      vHtml += '<td>';
      vHtml += '<td class="detail_value">';
      vHtml += '<span id="parent_folder_name"></span>';
      vHtml += '<input type="hidden" name="parent_folder_code">';
      vHtml += '</td>';
      vHtml += '</tr>';

      // Sort Setting
      vHtml += '<tr>';
      vHtml += '<td class="detail_name">';
      vHtml += MyLang.getMsg('TYPE_SORT_SETTING');
      vHtml += '<td>';
      vHtml += '<td class="detail_value">';
      vHtml += '<div id="render_folder_sort_setting"></div>';
      vHtml += '</td>';
      vHtml += '</tr>';

      vHtml += '</table>';

      // ここから下は、管理者画面でのみ表示
      vHtml += '<div id="show_only_in_admin_mode"';
      if (!aIsAdminMode) {
        vHtml += ' style="display:none;"';
      }
      vHtml += '>';

      vHtml += '<div id="priv_setting_panel_render_area" style="margin-top:3px;">';
      vHtml += '</div>';

      vHtml += '</div>';	// end show_only_in_admin_mode

      vHtml += '</form>';
      vHtml += '</div>';

      var formPanel = {
        xtype: 'panel',
        autoWidth: true,
        scrollable: true,
        html: vHtml,
        listeners: {
          afterRender: {
            fn: function () {
              var dataColSort = [], dataTypeSort = [];
              dataColSort.push(['file_name', MyLang.getMsg('COLUMN_DISPLAY_FILE_NAME')]);
              dataColSort.push(['created_date', MyLang.getMsg('COLUMN_DISPLAY_CREATED_DATE')]);
              dataTypeSort.push(['ASC', MyLang.getMsg('ASCENDING')]);
              dataTypeSort.push(['DESC', MyLang.getMsg('DESCENDING')]);

              var idFieldSet = 'form_fieldset_folder_sort';

              ExtMixins.destroyById(idFieldSet);
              new Ext.form.FieldSet({
                id: idFieldSet,
                renderTo: 'render_folder_sort_setting',
                autoWidth: true,
                border: false,
                layout: 'column',
                // style: 'background-color:white;padding:0;margin:0;border:none;',
                style: {
                  backgroundColor: 'white',
                  padding: 0,
                  margin: 0,
                  borderTop: 'none !important',
                },
                items: [
                  {
                    xtype: 'combo',
                    // fieldLabel: ' Column sort',
                    id: 'folder_col_sort',
                    triggerAction: 'all',
                    store: new Ext.data.ArrayStore({fields: ['value', 'name'], data: dataColSort}),
                    valueField: 'value',
                    displayField: 'name',
                    mode: 'local',
                    selectOnFocus: true,
                    editable: false,
                    value: 'file_name',
                    width: 130
                  }, {
                    xtype: 'combo',
                    // fieldLabel: ' Type sort',
                    id: 'folder_type_sort',
                    triggerAction: 'all',
                    store: new Ext.data.ArrayStore({fields: ['value', 'name'], data: dataTypeSort}),
                    valueField: 'value',
                    displayField: 'name',
                    mode: 'local',
                    selectOnFocus: true,
                    editable: false,
                    value: 'ASC',
                    width: 80
                  }
                ]
              });
            }
          }
        }
      };

      var buttons = [];
      // 保存または新規追加ボタン
      buttons.push(FolderDetailWindow.createSaveButton(aFolderCode, refreshCallback, aIsAdminMode, aCopyPrivOf));
      // カテゴリー削除ボタン
      if (aFolderCode != '__new_folder') {
        buttons.push(FolderDetailWindow.createMoveButton(aFolderCode, refreshCallback));

        buttons.push(FolderDetailWindow.createCopyButton(aFolderCode, refreshCallback));

        // 既存カテゴリーの表示の場合、削除ボタンも表示
        buttons.push(FolderDetailWindow.createDeleteButton(aFolderCode, refreshCallback));
        buttons.push('->');
      }
      // 閉じるボタン
      buttons.push({
        xtype: 'button',
        id: 'close_folder_window',
        iconCls: 'mdi mdi-close',
        text: MyLang.getMsg('MSG_CLOSE'),
        handler: function () {
          Ext.getCmp('window_doc_folder').close();
        }
      });

      // 詳細ウィンドウ
      var windowHeight = 240;
      if (aIsAdminMode) {
        // 管理者画面では、高さを560にする
        windowHeight = 610
      }
      var detailWindow = new Ext.Window({
        id: 'window_doc_folder',
        modal: true,
        width: DisplayMgr.adjustByViewportWidth(900),
        height: DisplayMgr.adjustByViewportHeight(windowHeight),
        bodyStyle: 'background-color:white;',
        title: title,
        plain: true,
        scrollable: false,
        layout: 'fit',
        items: [formPanel],
        buttons: buttons,
        listeners: {
          close: function () {
            FolderDetailWindow.folderDetail = null;
          }
        }
      });

      // ウィンドウを表示
      detailWindow.show();

      // 権限設定パネルを表示
      FolderDetailWindow.renderPrivSettingPanel();

      Ext.defer(function () {
        // アップロード権限の「一覧表示権限と同じ」チェックボックス変更のイベントハンドラ
        $('#folder_detail_form').find(':input[name=\'creatable_same_accessible\']').click(function () {
          FolderDetailWindow.enableCreatableInputsByCheck();
        });

        // ダウンロード権限の「一覧表示権限と同じ」チェックボックス変更のイベントハンドラ
        $('#folder_detail_form').find(':input[name=\'downloadable_same_accessible\']').click(function () {
          FolderDetailWindow.enableDownloadableInputsByCheck();
        });

        // 削除権限の「管理画面でのみ削除可能」チェックボックス変更のイベントハンドラをバインド
        $('#folder_detail_form').find(':input[name=\'deletable_admin_only\']').click(function () {
          FolderDetailWindow.enableDeletableInputsByCheck();
        });

        // 下位カテゴリー作成・削除権限の「一般ユーザーの下位カテゴリー作成・禁止を削除」チェックボックス変更のイベントハンドラをバインド
        $('#folder_detail_form').find(':input[name=\'subfolder_creatable_admin_only\']').click(function () {
          FolderDetailWindow.enableSubfolderCreatableInputsByCheck();
        });

        // ボタンをいったんDisable
        FolderDetailWindow.disableButtons();

        // カテゴリー詳細を表示
        if (aFolderCode == '__new_folder') {

          //// 新規カテゴリー追加の場合

          // パラメータで指定された親カテゴリー名を表示
          // その他の項目は空欄
          $('#folder_detail_form').find(':input[name=\'parent_folder_code\']').val(aParentFolderCode);
          if (aParentFolderCode == Constants.ROOT_FOLDER_CODE) {
            $('#parent_folder_name').text(MyLang.getMsg('NO_PARENT'));  // なし
            FolderDetailWindow.enableButtons();
          } else {
            DocFolderRequest.getById(aParentFolderCode, false, false, function (aResult) {
              FolderDetailWindow.enableButtons();
              if (aResult == null) {
                // no operation
              } else {
                var folderDetail = aResult.folder;
                $('#parent_folder_name').text(folderDetail.folder_name);
              }
            });
          }

          // アップロード権限「一覧表示権限と同じ」については、デフォルトでチェック状態にする
          $('#folder_detail_form').find(':input[name=\'creatable_same_accessible\']').attr('checked', 'checked');
          // チェックボックスの状態でテキストボックスのenableを変更
          FolderDetailWindow.enableCreatableInputsByCheck();

          // ダウンロード権限「一覧表示権限と同じ」については、デフォルトでチェック状態にする
          $('#folder_detail_form').find(':input[name=\'downloadable_same_accessible\']').attr('checked', 'checked');
          // チェックボックスの状態でテキストボックスのenableを変更
          FolderDetailWindow.enableDownloadableInputsByCheck();

          // 削除権限「管理画面でのみ削除可能」については、デフォルトでチェック状態にする
          $('#folder_detail_form').find(':input[name=\'deletable_admin_only\']').attr('checked', 'checked');
          // チェックボックスの状態でテキストボックスのenableを変更
          FolderDetailWindow.enableDeletableInputsByCheck();

          // 下位カテゴリー作成・削除権限「一般ユーザーの下位カテゴリー作成・削除を禁止」については、デフォルトでチェック状態にする
          $('#folder_detail_form').find(':input[name=\'subfolder_creatable_admin_only\']').attr('checked', 'checked');
          // チェックボックスの状態でテキストボックスのenableを変更
          FolderDetailWindow.enableSubfolderCreatableInputsByCheck();

          // // 「サテライトオフィス・電子帳簿保存法ファイルサーバーにファイルを保存」を選択状態にする
          // $('#folder_detail_form').find(':input[name=\'folder_type\']').val(['gae_blobstore']);

          // パネルのenableをセット
          FolderDetailWindow.setPanelEnabled();

          // カテゴリーコード入力欄にフォーカスをセット
          (function () {
            $('#folder_detail_form').find(':input[name=\'folder_code\']')[0].focus();
          }).defer(300);
        } else {
          DocFolderRequest.getById(aFolderCode, false, false, function (aJsondata) {
            var folderDetail = aJsondata.folder;
            FolderDetailWindow.folderDetail = folderDetail;

            $('#folder_code_render_area').text(folderDetail.folder_code);
            $('#folder_detail_form').find(':input[name=\'folder_code\']').val(folderDetail.folder_code);
            $('#folder_detail_form').find(':input[name=\'folder_name\']').val(folderDetail.folder_name);
            $('#folder_detail_form').find(':input[name=\'parent_folder_code\']').val(folderDetail.parent_folder_code);
            Ext.getCmp('folder_col_sort').setValue(folderDetail.folder_col_sort);
            Ext.getCmp('folder_type_sort').setValue(folderDetail.folder_type_sort);

            //// 1. 一覧表示権限

            // ユーザーメールアドレス指定アクセス権
            var accessibleUsers = folderDetail.accessible_users;
            if (accessibleUsers == '*') {
              accessibleUsers = '';
            }
            $('#folder_detail_form').find(':input[name=\'accessible_users\']').val(accessibleUsers);

            //// 2. ファイルアップロード権限

            // 一覧表示権限と同じ
            if (folderDetail.creatable_same_accessible) {
              $('#folder_detail_form').find(':input[name=\'creatable_same_accessible\']').attr('checked', 'checked');
            }
            // 「一覧表示権限と同じ」チェックボックスの状態でテキストボックスのenableを変更
            FolderDetailWindow.enableCreatableInputsByCheck();
            // アップロード権限（メールアドレス）
            var creatableUsers = folderDetail.creatable_users;
            if (creatableUsers == '*') {
              creatableUsers = '';
            }
            $('#folder_detail_form').find(':input[name=\'creatable_users\']').val(creatableUsers);

            //// 4. ダウンロード権限

            // 一覧表示権限と同じ
            if (folderDetail.downloadable_same_accessible) {
              $('#folder_detail_form').find(':input[name=\'downloadable_same_accessible\']').attr('checked', 'checked');
            }
            // 「一覧表示権限と同じ」チェックボックスの状態でテキストボックスのenableを変更
            FolderDetailWindow.enableDownloadableInputsByCheck();
            // アップロード権限（メールアドレス）
            var downloadableUsers = folderDetail.downloadable_users;
            if (downloadableUsers == '*') {
              downloadableUsers = '';
            }
            $('#folder_detail_form').find(':input[name=\'downloadable_users\']').val(downloadableUsers);

            //// 5. 削除権限

            // 管理画面でのみ削除可能
            if (folderDetail.deletable_admin_only) {
              $('#folder_detail_form').find(':input[name=\'deletable_admin_only\']').attr('checked', 'checked');
            }
            // 「管理画面でのみ削除可能」チェックボックスの状態でテキストボックスのenableを変更
            FolderDetailWindow.enableDeletableInputsByCheck();
            // 削除権限（メールアドレス）
            var deletableUsers = folderDetail.deletable_users;
            if (deletableUsers == '*') {
              deletableUsers = '';
            }
            $('#folder_detail_form').find(':input[name=\'deletable_users\']').val(deletableUsers);

            //// 6. 下位カテゴリー作成・削除権限

            // 一般ユーザーの下位カテゴリー作成・削除を禁止
            if (folderDetail.subfolder_creatable_admin_only) {
              $('#folder_detail_form').find(':input[name=\'subfolder_creatable_admin_only\']').attr('checked', 'checked');
            }
            // 「一般ユーザーの下位カテゴリー作成・削除禁止」のチェックボックスの状態でテキストボックスのenableを変更
            FolderDetailWindow.enableSubfolderCreatableInputsByCheck();
            // 下位カテゴリー作成・削除可能なユーザー／グループ
            var subfolderCreatableUsers = folderDetail.subfolder_creatable_users;
            if (subfolderCreatableUsers == '*') {
              subfolderCreatableUsers = '';
            }
            $('#folder_detail_form').find(':input[name=\'subfolder_creatable_users\']').val(subfolderCreatableUsers);

            // 親カテゴリーコード
            if (folderDetail.parent_folder_code == Constants.ROOT_FOLDER_CODE) {
              $('#parent_folder_name').text(MyLang.getMsg('NO_PARENT'));

              FolderDetailWindow.enableButtons();
            } else {
              // 親カテゴリー名を取得して終了
              DocFolderRequest.getById(folderDetail.parent_folder_code, false, false, function (aJsondata) {
                var folderDetail = aJsondata.folder;
                $('#parent_folder_name').text(folderDetail.folder_name);

                FolderDetailWindow.enableButtons();
              });
            }

            // 通知先メールアドレス
            $('#folder_detail_form').find(':input[name=\'notice_mails\']').val([folderDetail.notice_mails]);

            // パネルのenableをセット
            FolderDetailWindow.setPanelEnabled();
          });
        }
      }, 200);

    }
  };

  /**
   * CategoriesManager
   *
   */
  CategoriesManager = {
    store: null,
    dataRaw: [],

    _init: function () {
      CategoriesManager.store = CategoriesManager.createDataStore();
    },

    // METHOD:: Create

    /**
     * createDataStore
     *
     * ドキュメントのためのデータストアを作成
     *
     * @return {Object}
     */
    createDataStore: function () {
      var store = new Ext.data.ArrayStore({
        autoDestroy: true,
        storeId: 'categorie_grid_store',
        fields: [
          {name: 'id'},
          {name: 'name'},
          {name: 'txt_color'},
          {name: 'bg_color'},
          {name: 'sort_order'},
          {name: 'uploaded_date'},
          {name: 'buttons'}
        ]
      });

      store.setData(CategoriesManager.dataRaw)

      return store;
    },

    /**
     * createColsGrid
     *
     * @returns {Object}
     */
    createColumnsGrid: function () {
      var cols = [
        {
          hidden: true,
          dataIndex: 'categorie_id'
        },
        {
          header: MyLang.getMsg('SORT_ORDER'),
          hidden: true,
          width: 50,
          dataIndex: 'sort_order',
        },
        {
          header: MyLang.getMsg('NAME_CATEGORIE'),
          width: 200,
          dataIndex: 'name',
          renderer: function (value, cell, record) {
            var style = 'color: ' + record.get('txt_color') + ' !important;';
            style += ' background-color: ' + record.get('bg_color') + ' !important';
            return '<span class="name-categorie" style="' + style + '">' + value + '</span>';
          }
        },
        {
          id: 'uploaded_date',
          header: MyLang.getMsg('UPLOADED_DATE'),
          width: 200,
          dataIndex: 'uploaded_date'
        },
        {
          header: "",
          align: 'center',
          width: 50,
          dataIndex: 'categorie_id',
          renderer: function (value, cell, record) {
            return '<span class="mdi mdi-pencil collapse" onclick="CategorieMaintePanel.showWindowEdit(\'' + record.get('id') + '\')"></span>';
          }
        },
        {
          header: "",
          align: 'center',
          width: 50,
          dataIndex: 'categorie_id',
          renderer: function (value, cell, record) {
            return '<span class="mdi mdi-close collapse" onclick="CategorieMaintePanel.showWindowDelete(\'' + record.get('id') + '\')"></span>';
          }
        },
        {
          header: "",
          align: 'center',
          width: 100,
          dataIndex: 'buttons'
        }
      ]

      return {
        defaults: {
          menuDisabled: true,
          sortable: false
        },
        items: cols,
        getIndexById(id) {
          var items = this.items;
          var item = items.find(function (item) {
            return item.id == id;
          });
          return items.indexOf(item);
        },
      }
    },

    // METHOD:: Getter
    /**
     * getRecordById
     *
     * @param {string} id
     * @returns {object}
     */
    getRecordById: function (id) {
      return CategoriesManager.store.getById(id);
    },

    /**
     * getRecordByName
     *
     * @param {string} fieldName
     * @param {string} value
     * @returns {object}
     */
    getRecordByFieldName: function (fieldName, value) {
      return CategoriesManager.store.findRecord(fieldName, value);
    },

    /**
     * getDataItems
     *
     * @returns {Array}
     */
    getDataItems: function () {
      return CategoriesManager.store.getData().items;
    },

    /**
     * To html
     *
     * @param record
     */
    getVHtmlByID: function (record) {
      var vHtml = '';
      vHtml += '<span class="name-categorie" sort_order="' + record['sort_order'] + '" style="color:' + record['txt_color'] + '; background-color: ' + record['bg_color'] + '">'
      vHtml += '  ' + record['name'];
      vHtml += '</span>';

      return vHtml;
    },

    // METHOD:: Setter

    /**
     * Remove all data in store
     *
     */
    removeAllData: function () {
      CategoriesManager.store.removeAll();
    },

    /**
     * Set data to store
     *
     * @param {Array} data
     */
    setData: function (data) {
      var dataForStore = [];

      Ext.each(data, function () {
        dataForStore.push([
          this.id,
          this.name,
          this.txt_color,
          this.bg_color,
          this.sort_order,
          this.uploaded_date,
          CategoriesManager.buttonHtml(this.id, this.sort_order)
        ]);
      });

      CategoriesManager.dataRaw = data;
      if (CategoriesManager.store) {
        CategoriesManager.store.loadData(dataForStore);
      }
    },

    /**
     * Send request load data folder
     *
     * @param {callback} callback
     */
    loadData: function (callback) {
      CategorieRequest.getAll({}, function (response) {
        if (response.status == 'ok') {
          CategoriesManager.setData(response.data)
        }

        if (typeof (callback) == 'function') {
          callback(response.status)
        }
      });
    },

    /**
     * upRow
     *
     * @param {string} aFieldId
     * @param {string} sortOrder
     */
    upRow: function (aFieldId, sortOrder) {
      var saveSortByOptionBtn = Ext.getCmp('save_sort_order_option_btn');
      var store = CategoriesManager.store;

      var myIndex = store.find('id', aFieldId);
      var myRecord = store.getAt(myIndex);
      var mySortOrder = myRecord.get('sort_order');

      // 自分のソートオーダーより小さいなかで、最大のものを求める
      var maxSortOrder = -1;
      var foundField = null;
      store.each(function (aRecord) {
        if (aRecord.get('id') != aFieldId) {
          var sortOrder = aRecord.get('sort_order');
          if (sortOrder < mySortOrder) {
            if (maxSortOrder < sortOrder) {
              maxSortOrder = sortOrder;
              foundField = aRecord.get('id');
            }
          }
        }
      });
      // 自分の一つ上の行をソートオーダーを入れ替えて、再ソート
      if (foundField != null) {
        myRecord.set('sort_order', maxSortOrder);
        var index = store.find('id', foundField);
        store.getAt(index).set('sort_order', mySortOrder);
        store.sort('sort_order', 'ASC');
      }

      saveSortByOptionBtn.enable();
    },

    /**
     * downRow
     *
     * @param {string} aFieldId
     * @param {string} sortOrder
     */
    downRow: function (aFieldId, sortOrder) {
      var saveSortByOptionBtn = Ext.getCmp('save_sort_order_option_btn');
      var store = CategoriesManager.store;

      var myIndex = store.find('id', aFieldId);
      var myRecord = store.getAt(myIndex);
      var mySortOrder = myRecord.get('sort_order');

      // 自分のソートオーダーより大きいなかで、最小のものを求める
      var minSortOrder = 10000;
      var foundField = null;
      store.each(function (aRecord) {
        if (aRecord.get('id') != aFieldId) {
          var sortOrder = aRecord.get('sort_order');
          if (sortOrder > mySortOrder) {
            if (minSortOrder > sortOrder) {
              minSortOrder = sortOrder;
              foundField = aRecord.get('id');
            }
          }
        }
      });
      // 自分の一つ上の行をソートオーダーを入れ替えて、再ソート
      if (foundField != null) {
        myRecord.set('sort_order', minSortOrder);
        var index = store.find('id', foundField);
        store.getAt(index).set('sort_order', mySortOrder);
        store.sort('sort_order', 'ASC');
      }

      saveSortByOptionBtn.enable();
    },

    buttonHtml: function (aFieldId, sortOrder) {
      var vHtml = '';
      vHtml += '<span'
      vHtml += '  class="link_cmd mdi mdi-chevron-up mdi-18px" '
      vHtml += '  title="' + MyLang.getMsg('MOVE_UP') + '"'
      vHtml += '  onclick="CategoriesManager.upRow(\'' + aFieldId + '\', \'' + sortOrder + '\');"'
      vHtml += '>'
      vHtml += '</span>'

      vHtml += '<span'
      vHtml += '  class="link_cmd mdi mdi-chevron-down mdi-18px" '
      vHtml += '  title="' + MyLang.getMsg('MOVE_DOWN') + '"'
      vHtml += '  onclick="CategoriesManager.downRow(\'' + aFieldId + '\', \'' + sortOrder + '\');"'
      vHtml += '>'
      vHtml += '</span>'

      return vHtml;
    },
  };
  CategoriesManager._init();

  /**
   * TagsManager
   *
   */
  TagsManager = {
    store: null,
    dataRaw: [],

    _init: function () {
      TagsManager.store = TagsManager.createDataStore();
    },

    // METHOD:: Create

    /**
     * createDataStore
     *
     * ドキュメントのためのデータストアを作成
     *
     * @return {Object}
     */
    createDataStore: function () {
      var store = new Ext.data.ArrayStore({
        autoDestroy: true,
        fields: [
          {name: 'id'},
          {name: 'name'},
          {name: 'uploaded_date'}
        ]
      });
      store.loadData(TagsManager.dataRaw, false);

      return store;
    },

    // METHOD:: Getter
    /**
     * getRecordById
     *
     * @param {string} id
     * @returns {object}
     */
    getRecordById: function (id) {
      return TagsManager.store.getById(id);
    },

    /**
     * getDataItems
     *
     * @returns {Array}
     */
    getDataItems: function () {
      return TagsManager.store.getData().items;
    },

    /**
     * getAt
     *
     * @param {number} index
     */
    getAt: function (index) {
      return TagsManager.store.getAt(index);
    },

    /**
     * Get tag by name
     *
     * @param {string} nameTag
     * @returns {object}
     */
    getByName: function (nameTag) {
      var indexOf = TagsManager.store.findBy(function (record, id) {
        if (record.get('name') == nameTag) {
          return true;
        }
      });

      if (indexOf != -1) {
        return TagsManager.getAt(indexOf);
      }

      return null;
    },

    // METHOD:: Setter

    /**
     * Remove all data in store
     *
     */
    removeAllData: function () {
      TagsManager.store.clearData();
    },

    /**
     * Set data to store
     *
     * @param {Array} data
     * @param {boolean} isAppend
     */
    setData: function (data, isAppend) {
      TagsManager.dataRaw = data;
      if (TagsManager.store) {
        TagsManager.store.loadData(data, isAppend);
      }
    },

    /**
     * addTag
     *
     * @param {string} name
     * @param {string} id
     */
    addTag: function (name, id) {
      var tag = {
        'name': name,
      };

      if (typeof (id) != 'undefined') {
        tag['id'] = id;
      }

      TagsManager.dataRaw.push(tag);
      TagsManager.store.add(tag);
    },

    /**
     * Send request load data folder
     *
     * @param {callback} callback
     */
    loadData: function (callback) {
      CategorieRequest.getAllTag({}, function (response) {
        if (response.status == 'ok') {
          TagsManager.setData(response.data, false);
        }

        if (typeof (callback) == 'function') {
          callback(response.status)
        }
      });
    },

    /**
     * reloadData
     *
     * @param {callback} callback
     */
    reloadData: function (callback) {
      TagsManager.loadData(callback);
    },
  };
  TagsManager._init();

  /**
   * ClientsInfoManager
   *
   */
  ClientsInfoManager = {
    store: null,
    dataRaw: [],

    isUseMasterRef: false,

    _init: function () {
      ClientsInfoManager.store = ClientsInfoManager.createDataStore();
    },

    // METHOD:: Create

    /**
     * createDataStore
     *
     * ドキュメントのためのデータストアを作成
     *
     * @return {Object}
     */
    createDataStore: function () {
      var store = new Ext.data.ArrayStore({
        autoDestroy: true,
        fields: [
          {name: 'id'},
          {name: 'document_code'},
          {name: 'client_name'},
        ]
      });
      store.setData(ClientsInfoManager.dataRaw)

      return store;
    },

    // METHOD:: Getter

    /**
     * getRecordById
     *
     * @param {string} id
     * @returns {object}
     */
    getRecordById: function (id) {
      return ClientsInfoManager.store.getById(id);
    },

    /**
     * Get name client
     *
     * @param {string} id
     * @returns {object}
     */
    getNameClientById: function (id) {
      var record = ClientsInfoManager.getRecordById(id);
      if (record) {
        return ClientsInfoManager.getRecordById(id).get('client_name');
      }

      return 'Not define';
    },

    /**
     * getDataItems
     *
     * @returns {Array}
     */
    getDataItems: function () {
      return ClientsInfoManager.store.getData().items;
    },

    /**
     * getAt
     *
     * @param {number} index
     */
    getAt: function (index) {
      return ClientsInfoManager.store.getAt(index);
    },

    /**
     * getClientByDocCode
     *
     * @param {string} nameCode
     * @returns {object}
     */
    getClientByDocCode: function (nameCode) {
      var indexOf = ClientsInfoManager.store.findBy(function (record, id) {
        if (record.get('document_code') == nameCode) {
          return true;
        }
      });

      if (indexOf != -1) {
        return ClientsInfoManager.getAt(indexOf);
      }

      return null;
    },

    /**
     * getClientByDocCodeInStore
     *
     * @param {string} nameCode
     * @param {Ext.data.Store} store
     * @returns {object}
     */
    getClientByDocCodeInStore: function (nameCode, store) {
      var indexOf = store.findBy(function (record, id) {
        if (record.get('document_code') == nameCode) {
          return true;
        }
      });

      if (indexOf != -1) {
        return store.getAt(indexOf);
      }

      return null;
    },

    /**
     * getClientByName
     *
     * @param {string} nameClient
     * @returns {object}
     */
    getClientByName: function (nameClient) {
      var indexOf = ClientsInfoManager.store.findBy(function (record, id) {
        if (record.get('client_name') == nameClient) {
          return true;
        }
      });

      if (indexOf != -1) {
        return ClientsInfoManager.getAt(indexOf);
      }

      return null;
    },

    /**
     * getClientByNameInStore
     *
     * @param {string} nameClient
     * @param {Ext.data.Store} store
     * @returns {object}
     */
    getClientByNameInStore: function (nameClient, store) {
      var indexOf = store.findBy(function (record, id) {
        if (record.get('client_name') == nameClient) {
          return true;
        }
      });

      if (indexOf != -1) {
        return store.getAt(indexOf);
      }

      return null;
    },

    // METHOD:: Setter

    /**
     * Remove all data in store
     *
     */
    removeAllData: function () {
      ClientsInfoManager.store.clearData();
    },

    /**
     * Set data to store
     *
     * @param {Array} data
     * @param {boolean} isAppend
     */
    setData: function (data, isAppend) {
      ClientsInfoManager.dataRaw = data;
      if (ClientsInfoManager.store) {
        ClientsInfoManager.store.loadData(data);
      }
    },

    /**
     * addClient
     *
     * @param {string} name
     * @param {string} document_code
     * @param {string} id
     */
    addClient: function (name, document_code, id) {
      // when data client from data master, we can not add client
      if (ClientsInfoManager.isUseMasterRef) return;

      var client = {
        'client_name': name,
        'document_code': document_code,
      };

      if (typeof (id) != 'undefined') {
        client['id'] = id;
      }

      ClientsInfoManager.dataRaw.push(client);
      ClientsInfoManager.store.add(client);
    },

    /**
     * Send request load data folder
     *
     * @param {callback} callback
     */
    loadData: function (callback) {
      ClientInfoRequest.getAll({}, function (response) {
        if (response.status == 'ok') {
          ClientsInfoManager.isUseMasterRef = response.isusemasterref;
          ClientsInfoManager.setData(response.clientsinfo, false);
        }

        if (typeof (callback) == 'function') {
          callback(response.status)
        }
      });
    },

    reloadData: function (callback) {
      // ClientsInfoManager.removeAllData();
      ClientsInfoManager.loadData(callback);
    },
  };
  ClientsInfoManager._init();

  /**
   * WorkflowDocManager
   *
   */
  WorkflowDocManager = {

    // METHOD:: Getter
    /**
     * getNewId
     *
     * @param {callback} callback
     */
    getNewId: function (callback) {
      WorkflowDocRequest.getNewId({}, function (response) {
        if (typeof (callback) == 'function') {
          callback(response.workflow_doc_id)
        } else {
          console.error('NOT HAVE FUNC CALLBACK')
        }
      });
    },

    /**
     * getAll
     *
     * @param {object} postData
     * @param {callback} callback
     */
    getPaging: function (postData, callback) {
      WorkflowDocRequest.getAllDoc(postData, function (aJsondata) {
        if (typeof (callback) == 'function') {
          callback(aJsondata)
        }
      });
    },

    /**
     * getDoc
     *
     * @param {number} page
     * @param {number} num_per_page
     * @param {callback} callback
     */
    getDoc: function (page, num_per_page, callback) {
      var postData = {
        page: page,
        num_per_page: num_per_page,
        just_my_doc: false,
      };

      WorkflowDocManager.getPaging(postData, function (aJsondata) {
        callback(aJsondata.have_more_rows, aJsondata.workflow_docs)
      });
    },

    /**
     * getMyDoc
     *
     * @param {number} page
     * @param {number} num_per_page
     * @param {callback} callback
     */
    getMyDoc: function (page, num_per_page, callback) {
      var postData = {
        page: page,
        num_per_page: num_per_page,
        just_my_doc: true,
      };

      WorkflowDocManager.getPaging(postData, function (aJsondata) {
        callback(aJsondata)
      });
    },

    /**
     * getDocById
     *
     * @param {string} workflow_doc_id
     * @param {callback} callback
     */
    getDocById: function (workflow_doc_id, callback) {
      var postData = {
        workflow_doc_id: workflow_doc_id,
      }
      WorkflowDocRequest.requestGetDocById(postData, function (success, aJsondata, errorCode) {
        if (success) {
          callback(success, aJsondata, errorCode)
        } else {
          SateraitoUI.MessageBox({
            icon: Ext.MessageBox.ERROR,
            msg: MyLang.getMsgByCode(errorCode, MyLang.getMsg('MSG_ERROR_GET_DOC_BY_ID_ERROR')),
            buttons: Ext.Msg.OK,
            fn: function () {
              callback(false, null, errorCode);
            }
          });
        }
      });
    },

    /**
     * getDocByIdModeAdmin
     *
     * @param {string} workflow_doc_id
     * @param {string} key_filter_doc_deleted
     * @param {callback} callback
     */
    getDocByIdModeAdmin: function (workflow_doc_id, key_filter_doc_deleted, callback) {
      var postData = {
        workflow_doc_id: workflow_doc_id,
        key_filter_doc_deleted: key_filter_doc_deleted,
      }
      WorkflowDocRequest.requestGetDocByIdModeAdmin(postData, function (success, dataDoc, errorCode) {
        if (success) {
          callback(success, dataDoc, errorCode)
        } else {
          SateraitoUI.MessageBox({
            icon: Ext.MessageBox.ERROR,
            msg: MyLang.getMsgByCode(errorCode, MyLang.getMsg('MSG_ERROR_GET_DOC_BY_ID_ERROR')),
            buttons: Ext.Msg.OK,
          });
        }
      });
    },

    /**
     * searchPaging
     *
     * @param {object} paramSearch
     * @param {number} page
     * @param {number} num_per_page
     * @param {callback} callback
     */
    searchPaging: function (paramSearch, page, num_per_page, callback) {
      paramSearch['page'] = page;
      paramSearch['num_per_page'] = num_per_page;
      paramSearch['use_cache'] = Constants.USE_CACHE;

      var startTime = performance.now()
      WorkflowDocRequest.requestSearchDoc(paramSearch, function (aJsonData) {
        if (typeof (callback) == 'function') callback(aJsonData.have_more_rows, aJsonData.workflow_docs, aJsonData.cursor_web_safe_string);
        var endTime = performance.now()
        console.log('Call to searchPaging took '+ (endTime - startTime)/1000 +' seconds')
      });
    },

    /**
     * searchPaging
     *
     * @param {object} paramSearch
     * @param {number} page
     * @param {number} num_per_page
     * @param {callback} callback
     */
    searchPagingAdmin: function (paramSearch, page, num_per_page, callback) {
      paramSearch['page'] = page;
      paramSearch['num_per_page'] = num_per_page;
      paramSearch['use_cache'] = Constants.USE_CACHE;

      var startTime = performance.now()
      WorkflowDocRequest.requestSearchDocAdmin(paramSearch, function (aJsonData) {
        if (typeof (callback) == 'function') callback(aJsonData.have_more_rows, aJsonData.workflow_docs, aJsonData.cursor_web_safe_string);
        var endTime = performance.now()
        console.log('Call to searchPagingAdmin took '+ (endTime - startTime) / 1000 +' seconds')
      });
    },

    /**
     * checkImportCloudStorage
     *
     * @param {string} aIdDoc
     * @param {callback} callback
     */
    checkImportCloudStorage: function (aIdDoc, callback) {
      var postData = {
        workflow_doc_id: aIdDoc,
      };

      WorkflowDocRequest.checkImportCloudStorage(postData, function (aJsondata) {
        callback(aJsondata.is_finished)
      });
    },

    /**
     * checkProcessImportGGDrive
     *
     * @param {array} listGGFileId
     * @param {string} aIdDoc
     * @param {callback} callback
     */
    checkProcessImportGGDrive: function (listGGFileId, aIdDoc, callback) {
      var postData = {
        list_gg_drive_file_id: listGGFileId.join(Constants.KEY_SPLIT_RAW),
        key_split_raw: Constants.KEY_SPLIT_RAW,
        workflow_doc_id: aIdDoc,
      }
      WorkflowDocRequest.requestCheckProcessImportGGDrive(postData, function (response) {
        callback(response.status == 'ok', response.is_finished, response.success_files, response.failed_files);
      });
    },

    /**
     * handlerShowDetailDocById
     *
     * @param {string} workflowDocId
     * @param {object} option
     */
    handlerShowDetailDocById: function (workflowDocId, option) {
      var record = null;

      switch (MyPanel.tabActive) {
        // For tab All workflow document
        case WorkflowDocPanel.nameTab:
          record = WorkflowDocPanel.store.getById(workflowDocId);
          WorkflowDocPanel.isShowDetail = true;
          break;

        // For tab My workflow document
        case MyWorkflowDocPanel.nameTab:
          record = MyWorkflowDocPanel.store.getById(workflowDocId);
          MyWorkflowDocPanel.isShowDetail = true;
          break;

        // For tab Workflow document shared with me
        case SharedWithMePanel.nameTab:
          record = SharedWithMePanel.store.getById(workflowDocId);
          SharedWithMePanel.isShowDetail = true;
          break;
      }

      if (record) {
        var dataDoc = record.data;
        CreateWorkflowDocPanel.showWindowDetail(dataDoc);
      }
    },

    /**
     * getNameFieldByName
     *
     * @param nameFiled
     * @returns {String}
     */
    getNameFieldByName: function (nameFiled) {
      switch (nameFiled) {
        case 'workflow_doc_id':
          return MyLang.getMsg('');
        case 'folder_code':
          return MyLang.getMsg('FOLDER_SAVE');
        case 'categorie_id':
          return MyLang.getMsg('CATEGORY');
        case 'title':
          return MyLang.getMsg('TITLE');
        case 'user_email':
          return MyLang.getMsg('USER_EMAIL');
        case 'document_code':
          return MyLang.getMsg('DOCUMENT_CODE');
        case 'transaction_date':
          return MyLang.getMsg('TRANSACTION_DATE');
        case 'transaction_amount':
          return MyLang.getMsg('TRANSACTION_AMOUNT');
        case 'client_name':
          return MyLang.getMsg('CLIENT_NAME');
        case 'google_drive_folder_id':
          return MyLang.getMsg('GOOGLE_DRIVE_FOLDER_ID');
      }
    },

    // METHOD:: Setter
    /**
     * createDoc
     *
     * @param {object} dataPost
     * @param {callback} callback
     */
    createDoc: function (dataPost, callback) {
      dataPost.screen = MyPanel.nameScreen;

      WorkflowDocRequest.requestCreateWorkflowDoc(dataPost, function (response) {
        if (typeof (callback) == 'function') {
          callback(response.status == 'ok', response.data, response.error_code)
        } else {
          console.error('NOT HAVE FUNC CALLBACK')
        }
      });
    },

    /**
     * updateDoc
     *
     * @param {object} dataPost
     * @param {callback} callback
     */
    updateDoc: function (dataPost, callback) {
      dataPost.screen = MyPanel.nameScreen;

      WorkflowDocRequest.requestUpdateWorkflowDoc(dataPost, function (response) {
        if (typeof (callback) == 'function') {
          callback(response.status == 'ok', response.data, response.error_code)
        } else {
          console.error('NOT HAVE FUNC CALLBACK')
        }
      });
    },

    /**
     * getNewId
     *
     * @param {string} aIdDoc
     * @param {callback} callback
     */
    deleteDocTemp: function (aIdDoc, callback) {
      var postData = {
        workflow_doc_id: aIdDoc,
        lang: MyLang.getLocale()
      }
      WorkflowDocRequest.requestDeleteDocTemp(postData, function (response) {
        if (typeof (callback) == 'function') {
          callback(response.status == 'ok')
        } else {
          console.error('NOT HAVE FUNC CALLBACK')
        }
      });
    },

    /**
     * deleteDoc
     *
     * @param {string} aIdDoc
     * @param {callback} callback
     */
    deleteDoc: function (aIdDoc, callback) {
      var postData = {
        workflow_doc_id: aIdDoc,
        screen: MyPanel.nameScreen,
        lang: MyLang.getLocale()
      }
      WorkflowDocRequest.requestDeleteDoc(postData, function (response) {
        if (typeof (callback) == 'function') {
          callback(response.status == 'ok', response.error_code)
        } else {
          console.error('NOT HAVE FUNC CALLBACK')
        }
      });
    },

    /**
     * getLogTextData
     *
     * @param {string} aIdDoc
     * @param {callback} callback
     */
    getLogTextData: function (aIdDoc, callback) {
      var postData = {
        workflow_doc_id: aIdDoc,
        lang: MyLang.getLocale()
      }
      WorkflowDocRequest.requestGetLogTextData(postData, function (response) {
        if (typeof (callback) == 'function') {
          callback(response.status == 'ok', response.data.status, response.data.log_data)
        } else {
          console.error('NOT HAVE FUNC CALLBACK')
        }
      });
    }
  };

  /**
   * ワークフローユーザー（ユーザー情報に登録したユーザー）取得用
   */
  WorkflowUserManager = {
    // METHOD:: Getter

    /**
     * getToken
     *
     * @param {callback} callback
     */
    getToken: function (callback) {
      WorkflowUserRequest.requestToken(function (response) {
        callback(response.token)
      });
    }

    // METHOD:: Setter
  };

  /**
   * カテゴリーにファイルをアップロードするウィンドウ
   */
  UploadFileWindow = {
    idDialog: 'file_attach_to_window',
    uploadSuccess: false,

    /**
     * closeWindow
     *
     */
    closeWindow: function () {
      var dialog = Ext.getCmp(UploadFileWindow.idDialog);
      if (dialog) {
        dialog.close();
      }
    },

    /**
     * showWindow
     *
     * @param {string} aIdDoc
     * @param {string} folderCode
     * @param {callback} callback
     * @param {boolean} aModeAdmin
     * @returns {boolean}
     */
    showWindow: function (aIdDoc, folderCode, callback, aModeAdmin) {
      if (typeof(aModeAdmin) == 'undefined') {
        aModeAdmin = false;
      }

      // 既に表示されていたら、前面に出す
      var existingWindow = Ext.getCmp(UploadFileWindow.idDialog);
      if (!(typeof (existingWindow) == 'undefined' || existingWindow == null)) {
        existingWindow.toFront();
        return false;
      }

      // 読込中メッセージを表示
      SateraitoUI.showLoadingMessage();

      WorkflowUserManager.getToken(function (token) {
        // 読込中メッセージを消去
        SateraitoUI.clearMessage();

        UploadFileWindow._showWindow(aIdDoc, folderCode, token, callback, aModeAdmin);
      });

    },

    /**
     * _showWindow
     *
     * コメントにファイルを添付ウィンドウを表示する
     *
     * @param {string} aIdDoc
     * @param {string} folderCode
     * @param {string} token
     * @param {callback} callback
     * @param {boolean} aModeAdmin
     */
    _showWindow: function (aIdDoc, folderCode, token, callback, aModeAdmin) {
      var vHtml = '';
      vHtml += '<iframe src="' + SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/attach/fileupload';
      vHtml += '?token=' + token;
      vHtml += '&workflow_doc_id=' + aIdDoc;
      vHtml += '&folder_code=' + folderCode;
      vHtml += '&admin_mode=' + aModeAdmin;
      vHtml += '&screen=' + LoginMgr.screenName;
      vHtml += '&hl=' + SATERAITO_LANG;
      vHtml += '"';
      vHtml += ' style="width:100%;height:100%;">';
      vHtml += '</iframe>';

      var buttons = [];
      buttons.push({
        iconCls: 'mdi mdi-close',
        text: MyLang.getMsg('MSG_CLOSE'),
        handler: function () {
          UploadFileWindow.closeWindow();
        }
      });

      // 詳細ウィンドウ
      var detailWindow = new Ext.Window({
        id: UploadFileWindow.idDialog,
        width: DisplayMgr.adjustByViewportWidth(470),
        height: DisplayMgr.adjustByViewportHeight(250),
        modal: true,
        resizable: true,
        bodyStyle: 'background-color:white;',
        title: MyLang.getMsg('UPLOAD_FILES'),
        plain: true,
        scrollable: false,
        layout: 'fit',
        html: vHtml,
        // items: [formPanel],
        buttons: buttons,
        listeners: {
          close: function () {
            CreateWorkflowDocPanel.btnFileLocal.enable();

            // callback(UploadFileWindow.uploadSuccess);
          }
        }
      });

      UploadFileWindow.uploadSuccess = false;

      // ウィンドウを開く
      detailWindow.show();

      /**
       * callbackOnUploadFinish
       *
       * アップロードが完了した場合にキックされる
       */
      var callbackOnUploadFinish = function (e) {
        if (e.origin == SATERAITO_MY_SITE_URL) {

          if (('' + e.data) == 'before_upload') {
            Ext.getCmp(UploadFileWindow.idDialog).down('toolbar').hide();
          }

          if (('' + e.data) == 'new_file_attached') {
            UploadFileWindow.uploadSuccess = true;
            (function () {
              // 新規ファイルを添付した
              callback(true);

              if (window.removeEventListener) {
                // IE以外
                window.removeEventListener('message', callbackOnUploadFinish, false);
              } else if (window.attachEvent) {
                // IE8
                window.detachEvent('onmessage', callbackOnUploadFinish);
              }
            }).defer(500);
          }
        }
      };

      if (window.addEventListener) {
        // IE以外
        window.addEventListener('message', callbackOnUploadFinish, false);
      } else if (window.attachEvent) {
        // IE8
        window.attachEvent('onmessage', callbackOnUploadFinish);
      }
    },

    /**
     * showWindowTypeGGDrive
     *
     * @param {string} aIdDoc
     * @param {string} folderCode
     * @param {callback} callback
     * @returns {boolean}
     */
    showWindowTypeGGDrive: function (aIdDoc, folderCode, callback) {
      // 既に表示されていたら、前面に出す
      var existingWindow = Ext.getCmp(UploadFileWindow.idDialog);
      if (!(typeof (existingWindow) == 'undefined' || existingWindow == null)) {
        existingWindow.toFront();
        return false;
      }

      UploadFileWindow._showWindowTypeGGDrive(aIdDoc, folderCode, callback);
    },

    /**
     * _showWindow
     *
     * コメントにファイルを添付ウィンドウを表示する
     *
     * @param {string} aIdDoc
     * @param {string} folderCode
     * @param {callback} callback
     */
    _showWindowTypeGGDrive: function (aIdDoc, folderCode, callback) {
      var btnCheck = Ext.create({
        xtype: 'button',
        text: MyLang.getMsg('CHECK_AND_SAVE'),
        iconCls: 'mdi mdi-check',
        handler: function (button) {

          var urlGGDrive = Ext.getCmp('txt_google_drive_id').getValue().trim();
          // Get id folder from URL google drive
          var ggDirveId = UploadFileWindow.getIdInUrlGGDirve(urlGGDrive);

          if (ggDirveId && ggDirveId != '') {
            button.disable();
            btnClose.disable();

            detailWindow.setLoading(true);
            FileflowDocManager.checkGoogleDirveIDAndStartImport(ggDirveId, aIdDoc, folderCode, function (success, errorCode, files) {
              if (success) {
                UploadFileWindow.handlerShowProcessUpload(files, aIdDoc, ggDirveId, callback);
                detailWindow.close();
              } else {
                SateraitoUI.MessageBox({
                  icon: Ext.MessageBox.ERROR,
                  msg: MyLang.getMsgByCode(errorCode, MyLang.getMsg('MSG_GOOGLE_DRIVE_ID_ERROR')),
                  buttons: Ext.Msg.OK,
                  fn: function (res) {
                    button.enable();
                    btnClose.enable();
                  }
                });
              }

              detailWindow.setLoading(false);
            });
          } else {
            SateraitoUI.MessageBox({
              icon: Ext.MessageBox.ERROR,
              msg: MyLang.getMsg('URL_IS_NOT_DRIVE_FOLDER_ID'),
              buttons: Ext.Msg.OK,
              fn: function (res) {
              }
            });
          }
        }
      })
      var btnClose = Ext.create({
        xtype: 'button',
        text: MyLang.getMsg('MSG_CLOSE'),
        iconCls: 'mdi mdi-close',
        handler: function () {
          UploadFileWindow.closeWindow();
        }
      });
      var buttons = [btnCheck, btnClose];

      var formPanel = {
        xtype: 'panel',
        autoWidth: true,
        scrollable: false,
        padding: 5,
        items: [
          {
            xtype: 'label',
            cls: 'sateraito-label',
            text: MyLang.getMsg('LABEL_GOOGLE_DRIVE_FOLDER_URL'),
          },
          {
            xtype: 'textfield',
            id: 'txt_google_drive_id',
            width: '100%',
            margin: '5px 0 15px 0',
            // emptyText: MyLang.getMsg('EMPTY_TEXT_GOOGLE_DRIVE_FOLDER_URL'),
            hideLabel: true
          },
          {
            xtype: 'label',
            cls: 'description',
            html: MyLang.getMsg('EXP_SHOW_GOOGLE_DRIVE_FOLDER')
          },
          // {
          //   xtype: 'label',
          //   cls: 'process-linear',
          //   html: '<div class="wrap-linear"> <div class="linear"></div> </div>'
          // },
        ]
      };

      // 詳細ウィンドウ
      var detailWindow = new Ext.Window({
        id: UploadFileWindow.idDialog,
        width: DisplayMgr.adjustByViewportWidth(550),
        height: DisplayMgr.adjustByViewportHeight(250),
        modal: true,
        // resizable: false,
        bodyStyle: 'background-color:white;',
        title: MyLang.getMsg('UPLOAD_FILE_FROM_GOOGLE_DRIVE'),
        plain: true,
        scrollable: false,
        layout: 'fit',
        items: [formPanel],
        buttons: buttons,
        listeners: {
          afterrender: function () {
            Ext.defer(function () {
              Ext.getCmp('txt_google_drive_id').focus();
            }, 200);
          },
          close: function () {
            CreateWorkflowDocPanel.btnImportFromGGDrive.enable();
          }
        }
      });

      // ウィンドウを開く
      detailWindow.show();
    },

    // METHOD:: Handler
    handlerAfterGGDriveSuccess: function (aIdDoc, folderCode, ggDirveId, callback) {
      Ext.getCmp('txt_google_drive_id').addCls('processing');

      var processLinear = $('#' + UploadFileWindow.idDialog + ' .process-linear')[0];
      processLinear.classList.add('processing');

      WorkflowDocManager.checkImportCloudStorage(aIdDoc, function (isFinished) {
        if (isFinished == true) {
          Ext.defer(function () {
            callback(isFinished);
          }, 1000);
        } else {
          Ext.defer(function () {
            // Recheck after TIME_RECHECK_IMPORT_CLOUD_STORAGE second
            UploadFileWindow.handlerAfterGGDriveSuccess(aIdDoc, folderCode, ggDirveId, callback);
          }, Constants.TIME_RECHECK_IMPORT_CLOUD_STORAGE);
        }
      });
    },

    handlerShowProcessUpload: function (aIdDoc, callback) {
      // 詳細ウィンドウ
      var detailWindow = new Ext.Window({
        id: 'window_show_file_gg_drive_upload',
        width: DisplayMgr.adjustByViewportWidth(470),
        height: DisplayMgr.adjustByViewportHeight(250),
        modal: true,
        bodyStyle: 'background-color:white;',
        title: MyLang.getMsg('UPLOAD_FILES'),
        plain: true,
        scrollable: true,
        closeAccess: false,
        layout: 'fit',
        html: '<div id="container_file_gg_drive_upload"></div>',
        listeners: {
          afterrender: function (cmp) {
            if (typeof (callback) == 'function') {
              callback(cmp);
            }
          },
          beforeclose: function (cmpWin, event) {
            return cmpWin.closeAccess;
          }
        }
      });

      // ウィンドウを開く
      detailWindow.show();
    },

    handlerLoadFileProcessUpload: function (filesInfo, aIdDoc, callback) {
      for (var i = 0; i < filesInfo.length; i++) {
        var fileUpload = filesInfo[i];

        // 一つのファイルをアップロード
        var progress = document.createElement('div');
        progress.id = 'process_' + fileUpload.gg_drive_file_id;
        progress.className = 'info-file uploaded-0';

        if (!fileUpload.icon_url) {
          var iconClsEl = document.createElement('span');
          iconClsEl.className = DisplayMgr.getIconCls(fileUpload.file_name);
        } else {
          var iconClsEl = document.createElement('img');
          iconClsEl.src = fileUpload.icon_url;
        }

        var contentDivEl = document.createElement('div');
        contentDivEl.className = 'content';

        // Config element content Left
        var contentLeftEl = document.createElement('div');
        contentLeftEl.className = 'content-left';

        var nameFileEl = document.createElement('div');
        nameFileEl.className = 'name-file';
        nameFileEl.innerHTML = '<span>' + fileUpload.file_name + '</span>'

        var sizeFileEl = document.createElement('div');
        sizeFileEl.className = 'size-file';
        sizeFileEl.textContent = MyUtil.formatSizeUnits(fileUpload.file_size);

        contentLeftEl.append(nameFileEl);
        contentLeftEl.append(sizeFileEl);

        // Config element content Right
        var contentRightEl = document.createElement('div');
        contentRightEl.className = 'content-right';

        var progressEl = document.createElement('div');
        progressEl.className = 'content-complete'
        progressEl.textContent = '0%';
        contentRightEl.append(progressEl);

        contentDivEl.append(contentLeftEl);
        contentDivEl.append(contentRightEl);

        progress.append(iconClsEl);
        progress.append(contentDivEl);

        $('#container_file_gg_drive_upload')[0].append(progress);
      }

      // Handler check process sync file from google drive
      UploadFileWindow.handlerCheckProcessSyncGGDrive(filesInfo, aIdDoc, callback);
    },

    handlerCheckProcessSyncGGDrive: function (filesInfo, aIdDoc, callback) {
      var listGGFileId = [];
      for (var i = 0; i < filesInfo.length; i++) {
        listGGFileId.push(filesInfo[i].gg_drive_file_id);
      }

      var windowProcess = Ext.getCmp('window_show_file_gg_drive_upload');
      windowProcess.closeAccess = false;

      Ext.defer(function () {
        WorkflowDocManager.checkProcessImportGGDrive(listGGFileId, aIdDoc, function (success, isFinished, successFiles, failedFiles) {

          if (success) {
            for (var [key, value] of Object.entries(successFiles)) {
              if (value) {
                var processEl = document.getElementById('process_' + key);
                processEl.className = 'info-file uploaded-100 await';
                $(processEl).find('.content-complete').text('100%');
              }
            }
            for (var [key, value] of Object.entries(failedFiles)) {
              if (value) {
                var processEl = document.getElementById('process_' + key);
                processEl.className = 'info-file failed';
              }
            }

            if (isFinished) {
              windowProcess.closeAccess = true; // flag for before close window show process sync

              Ext.defer(function () {
                for (var i = 0; i < listGGFileId.length; i++) {
                  var processEl = document.getElementById('process_' + listGGFileId[i]);
                  processEl.classList.add('success');
                }
              }, 1000);
              Ext.defer(function () {
                Ext.getCmp('window_show_file_gg_drive_upload').close();
                callback(true);
              }, 2000);
            } else {
              windowProcess.closeAccess = false; // flag for before close window show process sync

              for (var [key, value] of Object.entries(successFiles)) {
                if (!value) {
                  var processEl = document.getElementById('process_' + key);
                  var uploaded = processEl.dataset.uploaded;
                  if (!uploaded) {
                    uploaded = MyUtil.randomBetween(1, 10);
                  } else {
                    uploaded = parseInt(uploaded)
                    uploaded_new = MyUtil.randomBetween(1, 5);
                    if ((uploaded + uploaded_new) < 90) {
                      uploaded = (uploaded + uploaded_new);
                    }
                  }

                  processEl.dataset.uploaded = uploaded;

                  processEl.className = 'info-file uploaded-'+ uploaded +' await';
                  $(processEl).find('.content-complete').text(uploaded + '%');
                  console.log(processEl.className)
                }
              }

              // Call recheck again
              UploadFileWindow.handlerCheckProcessSyncGGDrive(filesInfo, aIdDoc, callback);
            }
          }
        });
      }, Constants.TIME_RECHECK_IMPORT_CLOUD_STORAGE);
    },

    // METHOD:: Getter

    /**
     * getIdInUrlGGDirve
     *
     * @param {string} url
     * @returns {string}
     */
    getIdInUrlGGDirve: function (url) {
      var pathSplit = url.split('/');
      var pathId = pathSplit[pathSplit.length - 1].split('?');

      return pathId[0];
    },
  };

  /**
   * FileflowDocManager
   *
   */
  FileflowDocManager = {
    // METHOD:: Getter
    /**
     * getFileByIdDoc
     *
     * @param {string} docId
     * @param {boolean} isCreatingNewDoc
     * @param {boolean} adminMode
     * @param {callback} callback
     */
    getFileByDocId: function (docId, isCreatingNewDoc, adminMode, callback) {
      var dataPost = {
        workflow_doc_id: docId,
        is_creating_new_doc: isCreatingNewDoc,
      };
      FileflowDocRequest.requestGetFileByWorkflowDocId(dataPost, adminMode, function (response) {
        if (callback) {
          callback(response.files, response.is_runinig_sync)
        }
      })
    },

    /**
     * getInfoFileFromEmail
     *
     * @param {string} email
     * @param {string} message_id
     * @param {boolean} is_message_draft
     * @param {string} fileid
     * @param {string} fileName
     * @param {string} mimeType
     * @param {callback} callback
     */
    getInfoFilesFromEmail: function (email, message_id, is_message_draft, fileid, fileName, mimeType, callback) {
      var dataPost = {
        email: email,
        message_id: message_id,
        is_message_draft: is_message_draft,
        fileid: fileid,
        filename: fileName,
        mimetype: mimeType,
      };
      FileflowDocRequest.requestGetInfoFilesFromEmail(dataPost, function (response) {
        if (callback) {
          callback(response)
        }
      })
    },

    /**
     * getAttachmentFileGmail
     *
     * @param {string} access_token
     * @param {string} email
     * @param {string} message_id
     * @param {string} download_id
     * @param {callback} callback
     */
    getAttachmentFileGmail: function (access_token, email, message_id, download_id, callback) {
      var dataPost = {
        access_token: access_token,
        email: email,
        message_id: message_id,
        download_id: download_id,
      };
      FileflowDocRequest.requestAttachmentFileGmail(dataPost, function (response) {
        if (callback) {
          callback(response)
        }
      })
    },

    /**
     * getAccessToken
     *
     * @param {string} email
     * @param {callback} callback
     */
    getAccessToken: function (email, callback) {
      var dataPost = {
        email: email,
      };
      FileflowDocRequest.requestGetAccessToken(dataPost, function (response) {
        if (callback) {
          callback(response)
        }
      })
    },

    /**
     * getAccessToken
     *
     * @param {string} email
     * @param {callback} callback
     */
    getAccessTokenGGDrive: function (email, callback) {
      var dataPost = {
        email: email,
      };
      FileflowDocRequest.requestGetAccessTokenGoogleDrive(dataPost, function (response) {
        if (callback) {
          callback(response)
        }
      })
    },

    /**
     * getUploadUrlFromEmail
     *
     * @param {string} email
     * @param {string} folderId
     * @param {callback} callback
     */
    getUploadUrlFromEmail: function (email, folderId, callback) {
      var dataPost = {
        email: email,
        folder_id: folderId,
      };
      FileflowDocRequest.requestGetUploadUrlFromEmail(dataPost, function (response) {
        if (callback) {
          callback(response.upload_url)
        }
      })
    },

    /**
     * getMyFileShared
     *
     * @param {number} postData
     * @param {number} num_per_page
     * @param {callback} callback
     */
    getMyFileShared: function (postData, num_per_page, callback) {
      FileflowDocRequest.requestGetMyFileShared(postData, function (response) {
        callback(response)
      });
    },

    toHtmlForGrid: function (files, record) {
      if (files.length > 0) {
        var vHtml = '<span class="file-name link_cmd2">' + files[0].file_name + '</span>';
        if (files.length > 1) {
          var idElSubMoreFile = 'more_file_' + record.get('id');

          var htmlToolTip = '';
          for (var i = 0; i < files.length; i++) {
            htmlToolTip += '<li>' + files[i].file_name + '</li>';
          }

          vHtml += '<span class="more-file" id="' + idElSubMoreFile + '">';
          vHtml +=    (files.length) + MyLang.getMsg('TXT_MORE_FILE');
          vHtml += '</span>';

          var idTooltip = 'tooltipfor_' + idElSubMoreFile;
          Ext.defer(function () {
            var tooltipOld = Ext.getCmp(idTooltip);

            if (!tooltipOld) {
              Ext.create('Ext.tip.ToolTip', {
                id: idTooltip,
                target: idElSubMoreFile,
                html: htmlToolTip
              });
            } else {
              tooltipOld.setTarget(idElSubMoreFile);
            }
          }, 500);
        }
        return vHtml;
      }
    },

    toHtmlForGrid2: function (filesName, record) {
      if (filesName.length > 0) {
        var vHtml = '';
        if (filesName.length > 1) {
          var idElSubMoreFile = 'more_file_' + record.get('id');

          var htmlToolTip = '';
          for (var i = 0; i < filesName.length; i++) {
            htmlToolTip += '<li>' + filesName[i] + '</li>';
          }

          vHtml += '<span class="more-file" id="' + idElSubMoreFile + '">';
          vHtml +=    (filesName.length) + MyLang.getMsg('TXT_MORE_FILE');
          vHtml += '</span>';

          var idTooltip = 'tooltipfor_' + idElSubMoreFile;
          Ext.defer(function () {
            var tooltipOld = Ext.getCmp(idTooltip);

            if (!tooltipOld) {
              Ext.create('Ext.tip.ToolTip', {
                id: idTooltip,
                target: idElSubMoreFile,
                html: htmlToolTip
              });
            } else {
              tooltipOld.setTarget(idElSubMoreFile);
            }
          }, 500);
        }
        vHtml += ' <span class="file-name">' + filesName[0] + '</span>';

        return vHtml;
      }
    },

    /**
     * isImageFile
     *
     * ファイル名の拡張子から画像ファイルかどうかを判断する
     *
     * @param {string} aFileName
     * @return {boolean} true ... 画像ファイルである
     */
    isImageFile: function (aFileName) {
      var fileNameSplited = aFileName.split('.');
      if (fileNameSplited.length >= 2) {
        var extension = fileNameSplited[(fileNameSplited.length - 1)].toLowerCase();
        if (extension == 'png' || extension == 'jpg' || extension == 'jpeg' || extension == 'gif' || extension == 'bmp') {
          return true;
        }
      }
      return false;
    },

    // 添付ファイルをGoogleドライブでプレビューする
    openGoogleDocViewer: function(aElm){
      var file_id = $(aElm).attr('file_id');
      var is_pdf = $(aElm).attr('is_pdf');
      var is_image = $(aElm).attr('is_image');
      var app_id;
      if(typeof(APP_ID) == 'undefined'){
        app_id = LoginMgr.appId;
      }else{
        app_id = APP_ID;
      }

      var user_token;
      if (LoginMgr.token && LoginMgr.token != '') {
        user_token = LoginMgr.token;
      } else {
        if(typeof(USER_TOKEN) == 'undefined'){
          user_token = '';
        }else{
          user_token = USER_TOKEN;
        }
      }

      var urlReq = 'downloadattachedfile';
      if (MyPanel.nameScreen == Constants.SCREEN_ADMIN_CONSOLE) {
        urlReq = 'downloadattachedfileadmin'
      }

      var previewUrl = '';
      if (is_image == 'true' && user_token != '' && IS_TOKEN_MODE) {
        previewUrl += SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + app_id + '/attach/' + urlReq;
        previewUrl += '?token=' + user_token;
        previewUrl += '&hl=' + SATERAITO_LANG;
        previewUrl += '&file_id=' + encodeURIComponent(file_id);
        previewUrl += '&inline=1';
        previewUrl += '&action=view';
        previewUrl += '&screen=' + MyPanel.nameScreen
        previewUrl += '&mode=' + MyUtil.getMode();
      } else {
        // OpenID認証を使う
        previewUrl += SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + app_id + '/attach/oid/' + urlReq + '/' + encodeURIComponent(file_id);
        previewUrl += '?inline=1';
        previewUrl += '&action=view';
        previewUrl += '&screen=' + MyPanel.nameScreen
        previewUrl += '&hl=' + SATERAITO_LANG;
        previewUrl += '&mode=' + MyUtil.getMode();
      }
      window.open(previewUrl);

      // return;
      //
      // var openByGoogleDriveVeiwer;
      // if (Sateraito.Util.isSecurityBrowser() && Sateraito.Util.isIosSmartPhone()) {
      // //if (1 != 1) {
      //   // iOSのスマートフォン（iPhone, iPad, iPod）かつセキュリティブラウザの場合、OpenID認証を使って直接開く
      //   openByGoogleDriveVeiwer = false;
      // } else if (is_open_as_google_doc_viewer == 'true') {
      //   openByGoogleDriveVeiwer = true;
      // } else {
      //   openByGoogleDriveVeiwer = false;
      // }
      //
      // if(openByGoogleDriveVeiwer){
      //   // var win = window.open();
      //   window.goOpenUnBlockPopup = function(url){
      //     // win.location = url;
      //     // win.focus();
      //     var a = document.createElement('a');
      //     a.target = "blank"
      //     a.href = url;
      //     document.body.appendChild(a);
      //     a.click();
      //     document.body.removeChild(a);
      //   };
      //
      //   // ワンタイムトークンを取得
      //   var forPreview = true;
      //   AppsUser.requestOneTimeToken(app_id, forPreview, function(jsonData){
      //     var token = jsonData.token;
      //     var previewUrl = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + app_id + '/attach/previewattachedfile';
      //     previewUrl += '?file_id=' + encodeURIComponent(file_id)
      //     previewUrl += '&ot_token=' + encodeURIComponent(token)
      //     previewUrl += '&hl=' + SATERAITO_LANG
      //     previewUrl += '&screen=' + MyPanel.nameScreen
      //     previewUrl += '&inline=' + 1
      //
      //     console.log(previewUrl);
      //
      //     var google_doc_viewer_link = '';
      //     if(ATTACHED_FILE_VIEWER_TYPE == 'OFFICEVIEWER'){
      //       google_doc_viewer_link = 'https://view.officeapps.live.com/op/view.aspx?src=' + encodeURIComponent(previewUrl);
      //     }else{
      //       google_doc_viewer_link = 'https://drive.google.com/viewer?hl=' + SATERAITO_LANG + '&url=' + encodeURIComponent(previewUrl);
      //     }
      //     window.goOpenUnBlockPopup(google_doc_viewer_link);
      //   });
      // }else{
      //   var urlReq = 'downloadattachedfile';
      //   if (MyPanel.nameScreen == Constants.SCREEN_ADMIN_CONSOLE) {
      //     urlReq = 'downloadattachedfileadmin'
      //   }
      //
      //   var google_doc_viewer_link = '';
      //   if (is_image == 'true' && user_token != '') {
      //     google_doc_viewer_link += SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + app_id + '/attach/' + urlReq;
      //     google_doc_viewer_link += '?token=' + user_token;
      //     google_doc_viewer_link += '&hl=' + SATERAITO_LANG;
      //     google_doc_viewer_link += '&file_id=' + encodeURIComponent(file_id);
      //     google_doc_viewer_link += '&inline=1';
      //     google_doc_viewer_link += '&mode=' + MyUtil.getMode();
      //   } else {
      //       // OpenID認証を使う
      //     google_doc_viewer_link += SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + app_id + '/attach/oid/' + urlReq + '/' + encodeURIComponent(file_id);
      //     google_doc_viewer_link += '?inline=1';
      //     google_doc_viewer_link += '&hl=' + SATERAITO_LANG;
      //     google_doc_viewer_link += '&mode=' + MyUtil.getMode();
      //   }
      //   window.open(google_doc_viewer_link);
      // }
    },

    // METHOD:: Setter
    /**
     * deleteFileByID
     *
     * @param {string} fileId
     * @param {string} screen
     * @param {callback} callback
     */
    deleteFileByID: function (fileId, screen, callback) {
      var dataPost = {
        file_id: fileId,
        screen: screen,
        lang: MyLang.getLocale()
      };
      FileflowDocRequest.requestDeleteFile(dataPost, function (response) {
        if (callback) {
          callback(response.status == 'ok', response.error_code)
        }
      })
    },

    /**
     * deleteFileByIDModeAdmin
     *
     * @param {string} fileId
     * @param {string} screen
     * @param {callback} callback
     */
    deleteFileByIDModeAdmin: function (fileId, screen, callback) {
      var dataPost = {
        file_id: fileId,
        screen: screen,
        lang: MyLang.getLocale()
      };
      FileflowDocRequest.requestDeleteFileAdmin(dataPost, function (response) {
        if (callback) {
          callback(response.status == 'ok')
        }
      })
    },

    /**
     * deleteListFileTempByDocId
     *
     * @param {object} dataPost
     * @param {callback} callback
     */
    deleteListFileTempByDocId: function (dataPost, callback) {
      FileflowDocRequest.requestDeleteListFileTemp(dataPost, function (response) {
        if (callback) {
          callback(response.status == 'ok')
        }
      })
    },

    /**
     * deleteListFileTempByDocIdInPopup
     *
     * @param {string} workflow_doc_id
     * @param {array} listFileIdDelete
     * @param {string} email
     * @param {callback} callback
     */
    deleteListFileTempByDocIdInPopup: function (workflow_doc_id, listFileIdDelete, email, callback) {
      var dataPost = {
        workflow_doc_id: workflow_doc_id,
        list_id_file_delete: listFileIdDelete.join(Constants.KEY_SPLIT_RAW),
        email: email,
        key_split_raw: Constants.KEY_SPLIT_RAW,
        lang: MyLang.getLocale()
      };
      FileflowDocRequest.requestDeleteListFileTempInPopup(dataPost, function (response) {
        if (callback) {
          callback(response.status == 'ok')
        }
      })
    },

    /**
     * deleteListFileTempByFileIdInPopup
     *
     * @param {array} listFileId
     * @param {string} workflowDocId
     * @param {string} email
     * @param {callback} callback
     */
    deleteListFileTempByFileIdInPopup: function (listFileId, workflowDocId, email, callback) {
      var dataPost = {
        list_file_id: listFileId.join(Constants.KEY_SPLIT_RAW),
        key_split_raw: Constants.KEY_SPLIT_RAW,
        workflow_doc_id: workflowDocId,
        email: email,
        lang: MyLang.getLocale()
      };
      FileflowDocRequest.requestDeleteListFileTempByFileIdInPopup(dataPost, function (response) {
        if (callback) {
          callback(response.status == 'ok')
        }
      })
    },

    /**
     * checkGoogleDirveIDAndStartImport
     *
     * @param {array} listTypeFolder
     * @param {array} listTypeDoc
     * @param {string} aIdDoc
     * @param {string} folderCode
     * @param {boolean} adminMode
     * @param {callback} callback
     */
    checkGoogleDirveIDAndStartImport: function (listTypeFolder, listTypeDoc, aIdDoc, folderCode, adminMode, callback) {
      var self = this;
      var listGGFileID = [];
      for (var i = 0; i < listTypeDoc.length; i++) {
        listGGFileID.push(listTypeDoc[i].gg_drive_file_id);
      }

      var postData = {
        list_folder_id_gg_drive: Ext.encode(listTypeFolder),
        list_file_info_gg_drive: Ext.encode(listTypeDoc),
        list_file_id_gg_drive: Ext.encode(listGGFileID),
        workflow_doc_id: aIdDoc,
        folder_code: folderCode,
        screen: MyPanel.nameScreen,
        lang: MyLang.getLocale()
      }

      UploadFileWindow.handlerShowProcessUpload(aIdDoc, function (dialogProcess) {
        dialogProcess.setLoading(true);

        // When a folder in the list is selected
        if (listTypeFolder.length > 0 || listTypeDoc.length > 30) {
          FileflowDocRequest.requestInitializeParamsImport(postData, adminMode, function (success, importId, errorCode) {
            if (success) {
              Ext.defer(function () {
                self.handlerCheckAndShowParamsImport(aIdDoc, importId, dialogProcess, callback)
              }, Constants.TIME_RECHECK_IMPORT_CLOUD_STORAGE);
            } else {
              callback(false, errorCode, []);
            }
          });

        } else {
          // When no folder in the list is selected
          FileflowDocRequest.requestImportListFile(postData, adminMode, function (success, errorCode) {
            if (success) {
              UploadFileWindow.handlerLoadFileProcessUpload(listTypeDoc, aIdDoc, callback);
              dialogProcess.setLoading(false);
            } else {
              // Stop:: Stop check params import becau something error
              dialogProcess.closeAccess = true;
              dialogProcess.close();
              callback(false, errorCode, []);
            }
          });
        }
      });
    },

    /**
     * handlerCheckAndShowParamsImport
     *
     * @param aIdDoc
     * @param importId
     * @param dialogProcess
     * @param callback
     */
    handlerCheckAndShowParamsImport: function (aIdDoc, importId, dialogProcess, callback) {
      var self = this;

      FileflowDocRequest.requestCheckAndGetAllFileImport(importId, function (success, importStatus, dataFiles, errorCode) {
        if (success) {
          if (importStatus == 'success') { // Stop continue:: Has info files -> show process sync data files selected
            // convert list file upload
            UploadFileWindow.handlerLoadFileProcessUpload(dataFiles, aIdDoc, callback);
            dialogProcess.setLoading(false);
          } else if (importStatus != 'error') { // Continue:: check and get info all files in param import

            Ext.defer(function () {
              self.handlerCheckAndShowParamsImport(aIdDoc, importId, dialogProcess, callback);
            }, Constants.TIME_RECHECK_IMPORT_CLOUD_STORAGE);

          } else { // Stop:: Stop check params import becau something error

            dialogProcess.closeAccess = true;
            dialogProcess.close();
            callback(false, errorCode, []);
          }
        } else { // Stop:: Stop check params import becau something error

          dialogProcess.closeAccess = true;
          dialogProcess.close();
          callback(false, errorCode, []);
        }
      });
    },

    /**
     * updateFiles
     *
     * @param idsFile
     * @param folderCode
     * @param workFolowDocId
     * @param callback
     */
    updateFiles: function (idsFile, folderCode, workFolowDocId, callback) {
      idsFile = idsFile.join(Constants.KEY_SPLIT_RAW)

      var postData = {
        ids_file: idsFile,
        folder_code: folderCode,
        workflow_doc_id: workFolowDocId,
        key_split_raw: Constants.KEY_SPLIT_RAW,
        lang: MyLang.getLocale()
      }
      FileflowDocRequest.requestUpdateFiles(postData, function (response) {
        callback(response.status == 'ok');
      });
    },
  };

  /**
   * FolderSelectedWindow
   *
   */
  FolderSelectedWindow = {
    treepanel: null,
    btnAddFolder: null,
    btnDeleteFolder: null,
    toolbarTop: null,

    /**
     * onSelectClick
     *
     * @param {callback} onSelect
     * @param {boolean} includeRoot
     */
    onSelectClick: function (onSelect, includeRoot) {
      var folderTree = Ext.getCmp('selected_folder_tree_panel');
      var selectionModel = folderTree.selModel;
      var selectedNode = selectionModel.getSelected().getAt(0);

      var folderCode = '';
      var folderName = '';
      var fullPathFolder = '';

      if (selectedNode == null || typeof (selectedNode) == 'undefined') {
        if (includeRoot == true) {
          folderName = Constants.ROOT_FOLDER_NAME;
          folderCode = Constants.ROOT_FOLDER_CODE;
          fullPathFolder = '/' + folderName;
        } else {
          // 選択されていない
          SateraitoUI.MessageBox({
            icon: Ext.MessageBox.ERROR,
            msg: MyLang.getMsg('SELECT_SOMETHING').replace(/%1/g, OtherSetting.wordingForFolder),
            fn: function () {
            }
          });
          return;
        }
      } else {
        folderCode = selectedNode.data['folderCode'];
        folderName = selectedNode.data['folderName'];
        fullPathFolder = selectedNode.data['fullPathFolder'];
      }

      if (typeof (onSelect) == 'function') {
        onSelect(folderCode, folderName, fullPathFolder);
      }

      Ext.getCmp('folder_selected_window').close();
    },

    handlerItemClick: function (treepanel, record, el, index) {
      var isSubFolderCreatable = record.getData()['isSubFolderCreatable'];
      var isDeletableFolder = record.getData()['isDeletableFolder'];

      FolderSelectedWindow.btnAddFolder.disable();
      FolderSelectedWindow.btnDeleteFolder.disable();

      if (isSubFolderCreatable) {
        FolderSelectedWindow.btnAddFolder.enable();
      }
      if (isDeletableFolder) {
        FolderSelectedWindow.btnDeleteFolder.enable();
      }
    },

    /**
     * buildFolderTree
     *
     * カテゴリーツリーを再描画
     */
    buildFolderTree: function () {
      var folderTreePanel = Ext.getCmp('selected_folder_tree_panel');
      var rootNode = folderTreePanel.getRootNode();

      // ルート下のノードをいったん全削除
      rootNode.removeAll();
      // アペンド済みフラグをリセット
      rootNode.data['appended'] = false;

      // ルート下のノードを追加
      rootNode.loadAndAppendChildFolderNode(rootNode);
    },

    /**
     * createTBarTop
     *
     */
    createTBarTop: function () {
      FolderSelectedWindow.btnAddFolder = Ext.create({
        xtype: 'button',
        text: MyLang.getMsg('TXT_ADD_FOLDER'),
        iconCls: 'mdi mdi-folder-plus-outline',
        disabled: true,
        handler: function () {
          // 左側ツリーで選択中のカテゴリーを取得
          var folderTree = FolderSelectedWindow.treepanel;
          var selectionModel = folderTree.getSelectionModel();
          var selectedNode = selectionModel.getSelected().getAt(0);
          var folderCode = selectedNode.data['folderCode'];

          // 下位カテゴリー追加画面を表示
          var isAdminMode = (MyPanel.nameScreen == Constants.SCREEN_ADMIN_CONSOLE);
          FolderDetailWindow.showWindow('__new_folder', folderCode, function () {

            // ツリーのリフレッシュ（追加したカテゴリーの表示）

            // step1. 選択中のカテゴリーの下位カテゴリーを全て削除
            var isExpanded = selectedNode.isExpanded();
            while (selectedNode.hasChildNodes()) {
              selectedNode.removeChild(selectedNode.firstChild);
            }
            selectedNode.data['appended'] = false;
            folderTree.collapseNode(selectedNode);

            // step2. 選択中のカテゴリーの下位カテゴリーを取得して追加
            if (isExpanded) {
              folderTree.expandNode(selectedNode);
              // selectedNode.expand();
            }
          }, isAdminMode, folderCode);
        }
      });
      FolderSelectedWindow.btnDeleteFolder = Ext.create({
        xtype: 'button',
        text: MyLang.getMsg('TXT_DELETE_FOLDER'),
        iconCls: 'mdi mdi-folder-remove-outline',
        disabled: true,
        handler: function () {
          // 左側ツリーで選択中のカテゴリーを取得
          var folderTree = FolderSelectedWindow.treepanel;
          var selectionModel = folderTree.getSelectionModel();
          var selectedNode = selectionModel.getSelected().getAt(0);
          var folderCode = selectedNode.data['folderCode'];
          var folderName = selectedNode.data['folderName'];
          var parentFolderNode = selectedNode.parentNode;

          // 確認メッセージを出して削除実行
          Ext.Msg.show({
            icon: Ext.MessageBox.QUESTION,
            msg: MyLang.getMsg('CONFIRM_DELETE_SOMETHING').replace('%1', OtherSetting.wordingForFolder),
            buttons: Ext.Msg.OKCANCEL,
            fn: function (buttonId) {
              if (buttonId == 'ok') {

                // 削除実行
                var adminMode = false;
                DocFolderManager.delete([folderCode], function (success, errorCode) {
                  if (success) {
                    // 親カテゴリーの子供を全ていったん削除
                    var isExpanded = parentFolderNode.isExpanded();
                    while (parentFolderNode.hasChildNodes()) {
                      parentFolderNode.removeChild(parentFolderNode.firstChild);
                    }
                    parentFolderNode.data['appended'] = false;

                    // 親カテゴリーを選択
                    folderTree.setSelection(parentFolderNode);
                    folderTree.collapseNode(parentFolderNode);

                    // 選択されただけではカテゴリークリック時イベントハンドラが実行されないのでキックする
                    // parentFolderNode.folderNodeClicked(parentFolderNode);

                    if (isExpanded) {
                      folderTree.expandNode(parentFolderNode);
                    }
                  } else {
                    SateraitoUI.MessageBox({
                      icon: Ext.MessageBox.ERROR,
                      msg: MyLang.getMsgByCode(errorCode,MyLang.getMsg('MSG_DELETE_FAILED')),
                      fn: function () {
                      }
                    });
                  }
                }, adminMode);
              }
            }
          });
        }
      });

      var items = [FolderSelectedWindow.btnAddFolder, FolderSelectedWindow.btnDeleteFolder];
      FolderSelectedWindow.toolbarTop = Ext.create({
        xtype: 'toolbar',
        dock: 'top',
        cls: 'toolbar-badge',
        enableOverflow: true,
        items: items
      });

      return FolderSelectedWindow.toolbarTop;
    },

    /**
     * showWindow
     *
     * ユーザー・グループ検索用ウィンドウを表示する
     *
     * @param {event} onSelect
     * @param {string} action
     * @param {boolean} includeRoot
     * @param {string} title
     * @param {boolean} showTBar
     */
    showWindow: function (onSelect, action, includeRoot, title, showTBar) {
      if (typeof(showTBar) == 'undefined') {
        showTBar = true;
      }

      // 既に表示されていたら、前面に出す
      var existingWindow = Ext.getCmp('folder_selected_window');
      if (!(typeof (existingWindow) == 'undefined' || existingWindow == null)) {
        existingWindow.toFront();
        return;
      }

      // カテゴリーツリーのルートノードを生成
      treeRootFolderCode = Constants.ROOT_FOLDER_CODE;

      var rootNode = new FolderNodeForSelectWindow({
        action: action,
        text: 'root',
        folderName: '',
        folderCode: treeRootFolderCode,
        parentFolderCode: ''
      });

      var tbarTop = FolderSelectedWindow.createTBarTop();

      // 表示更新ボタン
      var refreshButton = {
        xtype: 'button',
        cls: 'base-mdi-circle',
        iconCls: 'mdi mdi-refresh',
        handler: function () {
          // カテゴリーツリーを再構築
          FolderSelectedWindow.buildFolderTree();
        }
      };
      var selectButton = {
        xtype: 'button',
        iconCls: 'mdi mdi-check',
        text: MyLang.getMsg('SELECT'),
        handler: function () {
          FolderSelectedWindow.onSelectClick(onSelect, includeRoot);
        }
      };
      var closeButton = {
        xtype: 'button',
        iconCls: 'mdi mdi-close',
        text: MyLang.getMsg('CANCEL'),
        handler: function () {
          Ext.getCmp('folder_selected_window').close();
        }
      };

      // カテゴリーのツリーパネル
      var folderTreePanel = {
        xtype: 'treepanel',
        region: 'center',
        id: 'selected_folder_tree_panel',
        cls: 'folder-tree-panel',
        rootVisible: false,
        root: rootNode,
        useArrows: true,
        scrollable: true,
        animate: true,
        collapsed: false,
        tbar: tbarTop,
        listeners: {
          afterrender: function (treepanel) {
            FolderSelectedWindow.treepanel = treepanel;
          },
          itemexpand: function (node, e) {
            if (node.data.listeners && node.data.listeners.expand) {
              node.data.listeners.expand(node);
            }
          },
          itemclick: FolderSelectedWindow.handlerItemClick
        }
      };

      if (!showTBar) {
        delete folderTreePanel.tbar;
      }

      if (typeof (title) == 'undefined') {
        title = OtherSetting.wordingForFolder;
      }

      var detailWindow = new Ext.Window({
        title: title,
        id: 'folder_selected_window',
        layout: 'border',
        width: DisplayMgr.adjustByViewportWidth(500),
        height: DisplayMgr.adjustByViewportHeight(300),
        modal: true,
        border: false,
        items: [folderTreePanel],
        buttons: [refreshButton, '->', selectButton, closeButton]
      });

      // ウィンドウを表示
      detailWindow.show();
    },

    // By phuc@vnd.sateraito.co.jp
    idDialogWindow2: 'folder_selected_window_2',
    idWindowShowListFiles: 'window_show_list_files',

    dailogCmp: null,
    store: null,
    folderColSort: 'name',
    folderTypeSort: 'ASC',

    fullPath: null,
    folderActive: null,
    queueFolderAfter: [],
    queueFolderBefore: [],

    // Ext cmp
    dataViewListLayout: null,
    dataViewGridLayout: null,
    btnShowListLayout: null,
    btnShowGridLayout: null,
    btnGoHome: null,
    btnGoAfter: null,
    btnGoBefore: null,

    // METHOD:: Create

    /**
     * Create store
     *
     * @returns {Ext.data.ArrayStore}
     */
    createStore: function () {
      return FolderSelectedWindow.store = new Ext.data.ArrayStore({
        autoDestroy: true,
        fields: [
          {name: 'code'},
          {name: 'name'},
          {name: 'type_item'},
          {name: 'file_size'},
          {name: 'file_size_display'},
          {name: 'name_display'},
          {name: 'author_name'},
          {name: 'author_name_email_display'},
          {name: 'uploaded_date'},
          {name: 'del_flag'},
        ],
        // sorters: FolderSelectedWindow.folderColSort,
        // direction: FolderSelectedWindow.folderTypeSort
      });
    },

    /**
     * createTplDataView
     *
     * @returns {Ext.XTemplate}
     */
    createTplDataView: function () {
      return new Ext.XTemplate(
        '<ul>',
        ' <tpl for=".">',
        '   <tpl if="this.showTitleFolder(values, xindex)">',
        '     <div class="title">'+ MyLang.getMsg('TXT_FOLDERS') +'</div>',
        '   </tpl>',
        '   <tpl if="this.showTitleFile(values, xindex)">',
        '     <div class="title" style="clear:left!important;">'+ MyLang.getMsg('TXT_FILES') +'</div>',
        '   </tpl>',

        '   <tpl if="del_flag">',
        '     <li class="itemView file-deleted">',
        '   <tpl else>',
        '     <li class="itemView">',
        '   </tpl>',
        '     <div class="wrap-name {type_item}">',
        '       {name_display}',
        '     </div>',
        '   </li>',
        ' </tpl>',
        '</ul>',
        {
          nextTypeIsFile: function (record, index) {
            var beforeRecord = FolderSelectedWindow.store.getAt(index - 2);
            if (beforeRecord) {
              console.log(beforeRecord.get('type_item'), record['type_item'])
              return beforeRecord.get('type_item') != record['type_item'];
            }
            return false;
          },
          showTitleFolder: function (record, index) {
            if (index - 1 == 0 && record['type_item'] == 'folder') {
              return true;
            }
          },
          showTitleFile: function (record, index) {
            if (record['type_item'] == 'file') {
              var beforeRecord = FolderSelectedWindow.store.getAt(index - 2);
              if (!beforeRecord || beforeRecord.get('type_item') == 'folder') {
                return true;
              }
            }
          },
        }
      );
    },

    /**
     * createToolbarTop
     *
     * @returns {Array}
     */
    createToolbarTop: function (canHomePreNext, key_filter_doc_deleted, adminMode) {
      FolderSelectedWindow.btnShowListLayout = Ext.create({
        xtype: 'button',
        iconCls: 'mdi mdi-view-grid',
        hidden: true,
        tooltipType: 'title',
        handler: function (button) {
          button.hide();
          FolderSelectedWindow.handlerChangeLayoutView('list');
        }
      });
      FolderSelectedWindow.btnShowGridLayout = Ext.create({
        xtype: 'button',
        iconCls: 'mdi mdi-view-list',
        hidden: true,
        tooltipType: 'title',
        handler: function (button) {
          button.hide();
          FolderSelectedWindow.handlerChangeLayoutView('grid');
        }
      });

      FolderSelectedWindow.btnGoHome = Ext.create({
        xtype: 'button',
        iconCls: 'mdi mdi-home',
        border: false,
        // disabled: true,
        height: 30,
        handler: function (button) {
          if (FolderSelectedWindow.folderActive['folder_code'] == Constants.ROOT_FOLDER_CODE) {
            return;
          }

          FolderSelectedWindow.queueFolderAfter = [];
          FolderSelectedWindow.queueFolderBefore = [];

          FolderSelectedWindow.handlerLoadChildFolder({
            folder_code: Constants.ROOT_FOLDER_CODE,
            key_filter_doc_deleted: key_filter_doc_deleted
          }, [], adminMode);

        }
      });
      FolderSelectedWindow.btnGoAfter = Ext.create({
        xtype: 'button',
        border: false,
        disabled: true,
        height: 30,
        iconCls: 'mdi mdi-arrow-left-bold-circle-outline',
        handler: function () {
          var folder = FolderSelectedWindow.queueFolderBefore.splice(FolderSelectedWindow.queueFolderBefore.length - 1)[0];
          if (folder) {
            FolderSelectedWindow.queueFolderAfter.push(FolderSelectedWindow.folderActive);

            folder['key_filter_doc_deleted'] = key_filter_doc_deleted;
            FolderSelectedWindow.handlerLoadChildFolder({
              folder_code: folder['folder_code'],
              sort: folder['sort'],
              type_sort: folder['type_sort'],
              key_filter_doc_deleted: key_filter_doc_deleted
            }, [], adminMode);
          }
        }
      });
      FolderSelectedWindow.btnGoBefore = Ext.create({
        xtype: 'button',
        border: false,
        disabled: true,
        height: 30,
        iconCls: 'mdi mdi-arrow-right-bold-circle-outline',
        handler: function () {
          var folder = FolderSelectedWindow.queueFolderAfter.splice(FolderSelectedWindow.queueFolderAfter.length - 1)[0];
          if (folder) {
            FolderSelectedWindow.queueFolderBefore.push(FolderSelectedWindow.folderActive);

            folder['key_filter_doc_deleted'] = key_filter_doc_deleted;
            FolderSelectedWindow.handlerLoadChildFolder({
              folder_code: folder['folder_code'],
              sort: folder['sort'],
              type_sort: folder['type_sort'],
              key_filter_doc_deleted: key_filter_doc_deleted
            }, [], adminMode);
          }
        }
      });

      var itemTBar = [];
      if (canHomePreNext) {
        itemTBar.push(FolderSelectedWindow.btnGoHome);
        itemTBar.push(FolderSelectedWindow.btnGoAfter);
        itemTBar.push(FolderSelectedWindow.btnGoBefore);
      }

      itemTBar.push('->');
      itemTBar.push(FolderSelectedWindow.btnShowGridLayout);
      itemTBar.push(FolderSelectedWindow.btnShowListLayout);

      return itemTBar;
    },

    /**
     * createToolbarBottom
     *
     * @returns {Array}
     */
    createToolbarBottom: function (needRefresh, key_filter_doc_deleted, adminMode) {
      var itemBBar = [];

      if (needRefresh) {
        itemBBar.push({
          xtype: 'button',
          cls: 'base-mdi-circle',
          iconCls: 'mdi mdi-refresh',
          handler: function () {
            FolderSelectedWindow.handlerRefreshData(adminMode)
          }
        });
      }

      itemBBar.push('->');
      itemBBar.push({
        xtype: 'button',
        iconCls: 'mdi mdi-close',
        text: MyLang.getMsg('MSG_CLOSE'),
        handler: FolderSelectedWindow.handlerCloseWindow2
      });

      return itemBBar;
    },

    /**
     *createViewListLayout
     *
     * @returns {Ext.DataView}
     */
    createViewListLayout: function (store, adminMode) {
      var itemTpl = FolderSelectedWindow.createTplDataView();

      FolderSelectedWindow.dataViewListLayout = Ext.create({
        xtype: 'dataview',
        store: store,
        tpl: itemTpl,
        cls: 'folder-data-view list-file-upload',
        itemSelector: 'li.itemView',
        overClass: 'DataView-Hover',
        scrollable: true,
        hidden: true,
        listeners: {
          itemdblclick: function (layout, record, item, index, e) {
            FolderSelectedWindow.handlerOpenFolderOrFile(record, adminMode);
          }
        }
      });

      return FolderSelectedWindow.dataViewListLayout;
    },

    createColumns: function () {
      var columns = [
        {
          dataIndex: 'folder_code',
          hidden: true,
        },
        {
          header: MyLang.getMsg('FILE_NAME'),
          dataIndex: 'name_display',
          flex: 1,
          renderer: function (value, gridcell, record) {
          var vHtml = '';

          if (record.get('del_flag')) {
            vHtml += '<span class="file-deleted">';
          } else {
            vHtml += '<span>';
          }
          vHtml += value;
          vHtml += '</span>';

          return vHtml;
        }
        },
        {
          header: MyLang.getMsg('AUTHOR_NAME'),
          dataIndex: 'author_name_email_display',
          width: 150,
        },
        {
          header: MyLang.getMsg('TXT_LAST_MODIFIED'),
          dataIndex: 'uploaded_date',
          width: 150,
        },
        {
          header: MyLang.getMsg('FILE_SIZE'),
          dataIndex: 'file_size_display',
          width: 150,
        },
      ];

      return Ext.grid.ColumnModel({
        items: ExtMixins.convertColumns(columns),
        defaults: {
          menuDisabled: true,
          sortable: true
        }
      })
    },

    /**
     * createViewGridLayout
     *
     * @returns {Ext.grid}
     */
    createViewGridLayout: function (store, adminMode) {
      var columns = FolderSelectedWindow.createColumns();

      FolderSelectedWindow.dataViewGridLayout = Ext.create({
        xtype: 'grid',
        cls: 'grid-file-upload',
        store: store,
        columns: columns,
        scrollable: true,
        hidden: true,
        sortableColumns: false,
        listeners: {
          show: FolderSelectedWindow.handlerStyleGridFileUpload,
          itemdblclick: function (layout, record, item, index, e) {
            FolderSelectedWindow.handlerOpenFolderOrFile(record, adminMode);
          }
        }
      });

      return FolderSelectedWindow.dataViewGridLayout;
    },

    /**
     * showWindow2
     *
     * ユーザー・グループ検索用ウィンドウを表示する
     *
     * @param {string} folder_code
     * @param {string} key_filter_doc_deleted
     * @param {boolean} adminMode
     * @param {object} eventObj
     */
    showWindow2: function (folder_code, list_folder_code_get, key_filter_doc_deleted, adminMode, eventObj) {
      // 既に表示されていたら、前面に出す
      var existingWindow = Ext.getCmp(FolderSelectedWindow.idDialogWindow2);
      if (!(typeof (existingWindow) == 'undefined' || existingWindow == null)) {
        existingWindow.toFront();
        return false;
      }

      if (!key_filter_doc_deleted || key_filter_doc_deleted == '') {
        key_filter_doc_deleted = Constants.KEY_FILTER_NOT_DELETED_DOC;
      }

      // Init store
      FolderSelectedWindow.createStore();
      FolderSelectedWindow._showWindow2(folder_code, key_filter_doc_deleted, adminMode, eventObj);

      // Handler load data item in folder
      if (typeof (folder_code) == 'undefined') {
        folder_code = Constants.ROOT_FOLDER_CODE;
      }
      FolderSelectedWindow.handlerLoadChildFolder({folder_code, key_filter_doc_deleted}, list_folder_code_get, adminMode, function (success, fullPath, listFolderGet, data, errorCode) {
        // Call event afterLoad
        if (success && eventObj) {
          if (typeof (eventObj['afterLoad']) == 'function') {
            eventObj['afterLoad'](listFolderGet);
          }
        }
      });
    },

    /**
     * _showWindow2
     *
     * @param {string} folder_code
     * @param {string} key_filter_doc_deleted
     * @param {boolean} adminMode
     * @param {object} eventObj
     */
    _showWindow2: function (folder_code, key_filter_doc_deleted, adminMode, eventObj) {
      var tbarTop = FolderSelectedWindow.createToolbarTop(true, key_filter_doc_deleted, adminMode);
      var tbarBottom = FolderSelectedWindow.createToolbarBottom(true, key_filter_doc_deleted, adminMode);

      var dataViewListLayout = FolderSelectedWindow.createViewListLayout(FolderSelectedWindow.store, adminMode);
      var dataViewGridLayout = FolderSelectedWindow.createViewGridLayout(FolderSelectedWindow.store, adminMode);

      var title = MyLang.getMsg('MY_FOLDER');
      if (FolderSelectedWindow.fullPath) {
        title += FolderSelectedWindow.fullPath;
      }

      FolderSelectedWindow.dailogCmp = new Ext.Window({
        title: title,
        id: FolderSelectedWindow.idDialogWindow2,
        plain: true,
        autoScroll: false,
        layout: 'fit',
        width: DisplayMgr.adjustByViewportWidth(710),
        height: DisplayMgr.adjustByViewportHeight(400),
        modal: true,
        border: false,
        minWidth: 180,
        tbar: tbarTop,
        bbar: tbarBottom,
        items: [dataViewListLayout, dataViewGridLayout],
        listeners: {
          afterrender: function () {
            FolderSelectedWindow.handlerChangeLayoutView(LocalSettingsManager.settings.folderSelected.layout);
          },
          close: function (panel, eOpts) {
            FolderSelectedWindow.folderActive = null;
            FolderSelectedWindow.queueFolderAfter = [];
            FolderSelectedWindow.queueFolderBefore = [];

            FolderSelectedWindow.dailogCmp = null;
            FolderSelectedWindow.fullPath = null;
            FolderSelectedWindow.dataViewListLayout = null;
            FolderSelectedWindow.dataViewGridLayout = null;
            FolderSelectedWindow.btnShowListLayout = null;
            FolderSelectedWindow.btnShowGridLayout = null;
            FolderSelectedWindow.btnGoHome = null;
            FolderSelectedWindow.btnGoAfter = null;
            FolderSelectedWindow.btnGoBefore = null;

            // Call event close window
            if (eventObj) {
              if (typeof (eventObj['close']) == 'function') {
                eventObj['close']();
              }
            }
          },
          resize: function (windowCmp) {
            var windowWidth = windowCmp.getWidth()
            var countCol = 4;

            if (windowWidth <= 200) {
              countCol = 1;
            }
            if (windowWidth > 200 && windowWidth <= 400) {
              countCol = 2;
            }
            if (windowWidth > 400 && windowWidth <= 600) {
              countCol = 3;
            }
            if (windowWidth > 600 && windowWidth <= 920) {
              countCol = 4;
            }
            if (windowWidth > 920 && windowWidth <= 1320) {
              countCol = 5;
            }
            if (windowWidth >= 1320) {
              countCol = 6;
            }

            var width = (windowCmp.getWidth()) - (5 * (countCol * 2));

            $('.folder-data-view.list-file-upload .itemView').each(function (index, itemViewEl) {
              itemViewEl.style.width = (width/countCol) - 5 + 'px';
            });
          }
        }
      });

      // ウィンドウを表示
      FolderSelectedWindow.dailogCmp.show();
    },

    /**
     * showListFiles
     *
     * ユーザー・グループ検索用ウィンドウを表示する
     *
     * @param {array} files
     * @param {object} eventObj
     */
    showFilesList: function (files, eventObj) {
      // 既に表示されていたら、前面に出す
      var existingWindow = Ext.getCmp(FolderSelectedWindow.idWindowShowListFiles);
      if (!(typeof (existingWindow) == 'undefined' || existingWindow == null)) {
        existingWindow.toFront();
        return false;
      }
      // Handler load data item in folder
      if (typeof (files) == 'undefined') {
        return false;
      }

      // Init store
      FolderSelectedWindow.createStore();
      FolderSelectedWindow._showFilesList(files, eventObj);
      FolderSelectedWindow.putArrayToDataStore(files);
    },

    /**
     * _showListFiles
     *
     * @param {array} files
     * @param {object} eventObj
     */
    _showFilesList: function (files, eventObj) {
      var tbarTop = FolderSelectedWindow.createToolbarTop(false, false);
      var tbarBottom = FolderSelectedWindow.createToolbarBottom(false, false);

      var dataViewListLayout = FolderSelectedWindow.createViewListLayout(FolderSelectedWindow.store, false);
      var dataViewGridLayout = FolderSelectedWindow.createViewGridLayout(FolderSelectedWindow.store, false);

      var title = MyLang.getMsg('MY_FOLDER');
      if (FolderSelectedWindow.fullPath) {
        title += FolderSelectedWindow.fullPath;
      }

      FolderSelectedWindow.dailogCmp = new Ext.Window({
        title: title,
        id: FolderSelectedWindow.idDialogWindow2,
        plain: true,
        autoScroll: false,
        layout: 'fit',
        width: DisplayMgr.adjustByViewportWidth(710),
        height: DisplayMgr.adjustByViewportHeight(400),
        modal: true,
        border: false,
        minWidth: 180,
        tbar: tbarTop,
        bbar: tbarBottom,
        items: [dataViewListLayout, dataViewGridLayout],
        listeners: {
          afterrender: function () {
            FolderSelectedWindow.handlerChangeLayoutView(LocalSettingsManager.settings.folderSelected.layout);
          },
          close: function (panel, eOpts) {
            FolderSelectedWindow.folderActive = null;
            FolderSelectedWindow.queueFolderAfter = [];
            FolderSelectedWindow.queueFolderBefore = [];

            FolderSelectedWindow.dailogCmp = null;
            FolderSelectedWindow.fullPath = null;
            FolderSelectedWindow.dataViewListLayout = null;
            FolderSelectedWindow.dataViewGridLayout = null;
            FolderSelectedWindow.btnShowListLayout = null;
            FolderSelectedWindow.btnShowGridLayout = null;
            FolderSelectedWindow.btnGoHome = null;
            FolderSelectedWindow.btnGoAfter = null;
            FolderSelectedWindow.btnGoBefore = null;

            // Call event close window
            if (eventObj) {
              if (typeof (eventObj['close']) == 'function') {
                eventObj['close']();
              }
            }
          },
          resize: function (windowCmp) {
            var windowWidth = windowCmp.getWidth()
            var countCol = 4;

            if (windowWidth <= 200) {
              countCol = 1;
            }
            if (windowWidth > 200 && windowWidth <= 400) {
              countCol = 2;
            }
            if (windowWidth > 400 && windowWidth <= 600) {
              countCol = 3;
            }
            if (windowWidth > 600 && windowWidth <= 920) {
              countCol = 4;
            }
            if (windowWidth > 920 && windowWidth <= 1320) {
              countCol = 5;
            }
            if (windowWidth >= 1320) {
              countCol = 6;
            }

            var width = (windowCmp.getWidth()) - (5 * (countCol * 2));

            $('.folder-data-view.list-file-upload .itemView').each(function (index, itemViewEl) {
              itemViewEl.style.width = (width/countCol) - 5 + 'px';
            });
          }
        }
      });

      // ウィンドウを表示
      FolderSelectedWindow.dailogCmp.show();
    },

    // METHOD:: Handler

    /**
     * handlerCloseWindow2
     *
     * @returns {boolean}
     */
    handlerCloseWindow2: function () {
      // 既に表示されていたら、前面に出す
      var existingWindow = FolderSelectedWindow.dailogCmp;
      if (!(typeof (existingWindow) == 'undefined' || existingWindow == null)) {
        existingWindow.close();
        return false;
      }
    },

    handlerLoadChildFolder: function (folder, listFolderCodeGet, adminMode, callback) {
      var folderCode = folder['folder_code'];
      var folderColSort = folder['sort'];
      var folderTypeSort = folder['type_sort'];
      var keyFilterDocDeleted = folder['key_filter_doc_deleted'];

      FolderSelectedWindow.folderColSort = folderColSort;
      FolderSelectedWindow.folderTypeSort = folderTypeSort;

      // UI - Show animation loading in grid, lits
      FolderSelectedWindow.handlerSetLoading(true);

      // 自分の子カテゴリーを取得し、ノードとして追加する
      DocFolderRequest.getChildFileAndFolder(folderCode, keyFilterDocDeleted, listFolderCodeGet, adminMode, false, function (success, fullPath, listFolderGet, data, errorCode) {
        if (success) {
          FolderSelectedWindow.putArrayToDataStore(data);

          FolderSelectedWindow.folderActive = folder;
          FolderSelectedWindow.fullPath = fullPath;

          FolderSelectedWindow.handlerToolbarTop();
          FolderSelectedWindow.handlerTitle();

        } else {
          SateraitoUI.MessageBox({
            icon: Ext.MessageBox.ERROR,
            msg: MyLang.getMsgByCode(errorCode, MyLang.getMsg('MSG_ERROR_USER_ACCESSIBLE_INFO_NONE')),
            buttons: Ext.Msg.OK,
            fn: function (buttonId) {
              FolderSelectedWindow.handlerCloseWindow2();
            }
          });
        }

        if (typeof (callback) == 'function') {
          callback(success, fullPath, listFolderGet, data, errorCode);
        }

        // UI - Hide animation loading in grid, lits
        FolderSelectedWindow.handlerSetLoading(false);
      });
    },

    handlerRefreshData: function (adminMode) {
      FolderSelectedWindow.handlerLoadChildFolder(FolderSelectedWindow.folderActive, [], adminMode, function (success, fullPath, listParent, data, errorCode) {
      });
    },

    handlerOpenFolderOrFile: function (record, adminMode) {
      if (record.get('type_item') == 'folder') {
        // Clear queue folder before
        FolderSelectedWindow.queueFolderAfter = [];
        FolderSelectedWindow.queueFolderBefore.push(FolderSelectedWindow.folderActive);

        var folder = {
          folder_code: record.get('code'),
          key_filter_doc_deleted: FolderSelectedWindow.folderActive['key_filter_doc_deleted'],
          sort: record.get('folder_col_sort'),
          type_sort: record.get('folder_type_sort'),
        };

        FolderSelectedWindow.handlerLoadChildFolder(folder, [], adminMode);
      }
    },

    /**
     * handlerStyleGridFileUpload
     *
     */
    handlerStyleGridFileUpload: function () {
      var grid = FolderSelectedWindow.dataViewGridLayout;
      var cellsFileDeleted = $("#" + grid.id + " .file-deleted").closest(".x-grid-item");
      cellsFileDeleted.addClass('cell-file-deleted');
    },

    handlerToolbarTop: function () {
      if (FolderSelectedWindow.btnGoHome) {
        var disableGoHome = (FolderSelectedWindow.folderActive['folder_code'] == Constants.ROOT_FOLDER_CODE);
        FolderSelectedWindow.btnGoHome.setDisabled(disableGoHome);
      }

      if (FolderSelectedWindow.btnGoBefore) {
        var disableGoAfter = FolderSelectedWindow.queueFolderAfter.length <= 0;
        FolderSelectedWindow.btnGoBefore.setDisabled(disableGoAfter);
      }

      if (FolderSelectedWindow.btnGoAfter) {
        var disableGoBefore = FolderSelectedWindow.queueFolderBefore.length <= 0;
        FolderSelectedWindow.btnGoAfter.setDisabled(disableGoBefore);
      }
    },

    handlerTitle: function () {
      if (FolderSelectedWindow.dailogCmp) {
        var title = MyLang.getMsg('MY_FOLDER');

        if (FolderSelectedWindow.fullPath) {
          title += FolderSelectedWindow.fullPath;
        }

        FolderSelectedWindow.dailogCmp.setTitle(title);
      }
    },

    handlerSetLoading: function (isLoading) {
      if (FolderSelectedWindow.dataViewGridLayout.isHidden() == false) {
        FolderSelectedWindow.dataViewGridLayout.setLoading(isLoading);
      }
      if (FolderSelectedWindow.dataViewListLayout.isHidden() == false) {
        FolderSelectedWindow.dataViewListLayout.setLoading(isLoading);
      }
    },

    handlerChangeLayoutView: function (nameView) {
      LocalSettingsManager.setSettingLayoutShowFolder('layout', nameView);

      if (nameView == 'list') {
        FolderSelectedWindow.btnShowListLayout.hide();
        FolderSelectedWindow.btnShowGridLayout.show();

        FolderSelectedWindow.dataViewListLayout.show();
        FolderSelectedWindow.dataViewGridLayout.hide();
      } else if (nameView == 'grid') {
        FolderSelectedWindow.btnShowListLayout.show();
        FolderSelectedWindow.btnShowGridLayout.hide();

        FolderSelectedWindow.dataViewListLayout.hide();
        FolderSelectedWindow.dataViewGridLayout.show();
      }
    },

    // METHOD:: Getter

    // METHOD:: Setter

    /**
     * loadDataStore
     * @param {array} data
     * @param {boolean} append
     */
    loadDataStore: function (data, append) {
      if (typeof (append) == 'undefined') {
        append = false;
      }

      FolderSelectedWindow.store.loadData(data, append);
    },

    /**
     * putArrayToDataStore
     *
     * 配列データをデータストアにロードする
     *
     * @param {Array} data ロードする配列データ
     * @param {boolean} append
     */
    putArrayToDataStore: function (data, append) {
      // データ追加
      var dataSet = [];

      Ext.each(data, function (item, index) {
        var fileSizeDisplay = MyUtil.formatSizeUnits(item.file_size)
        var fileSize = item.file_size;

        if (item.type_item == Constants.TYPE_FOLDER) {
          fileSizeDisplay = '<span class="mdi mdi-minus"></span>'
        }

        var downloadLink = DisplayMgr.toDownloadLink(item.code, item.name, item.is_downloadable, fileSize, item.author_email,
          item.author_name, item.mime_type, item.icon_url, Sateraito.DateUtil.datetimeShorten(this.uploaded_date), item.folder_code,
          item.attachment_type, item.attach_link, item.type_item, item.attachment_id, item.publish_flag, item.del_flag);
        if (MyPanel.nameScreen == 'admin_console') {
          downloadLink = DisplayMgr.toAdminDownloadLink(item.code, item.name, item.is_downloadable, fileSize, item.author_email,
            item.author_name, item.mime_type, item.icon_url, Sateraito.DateUtil.datetimeShorten(this.uploaded_date), item.folder_code,
            item.attachment_type, item.attach_link, item.type_item, item.attachment_id, item.publish_flag, item.del_flag);
        }

        var updated_date = item.updated_date;
        if (updated_date) {
          updated_date = updated_date.split('+')[0];
        }

        dataSet.push([
          item.code,
          item.name,
          item.type_item,
          fileSize,
          fileSizeDisplay,
          downloadLink,
          item.author_name,
          DisplayMgr.toMailLink(item.author_email, item.author_name, true),
          updated_date,
          item.del_flag,
        ]);
      });

      // データストアにデータをロードし、グリッドに表示させる
      FolderSelectedWindow.loadDataStore(dataSet, append);

      FolderSelectedWindow.handlerStyleGridFileUpload();
    },
  };

  /**
   * UserInfoManager
   *
   */
  UserInfoManager = {
    userList: [],
    dataRaw: [],
    store: null,

    _init: function () {
      UserInfoManager.store = UserInfoManager.createDataStore();
    },

    // METHOD:: Create

    /**
     * createDataStore
     */
    createDataStore: function () {
      var store = new Ext.data.ArrayStore({
        fields: [
          {name: 'email'},
          {name: 'family_name'},
          {name: 'given_name'},
          {name: 'department'},
          {name: 'job_title'},
          {name: 'language'},
          {name: 'created_date'}
        ]
      });
      store.loadData(UserInfoManager.dataRaw);

      return store;
    },

    // METHOD:: Getter

    /**
     * WFUserList
     *
     * @param callback
     * @constructor
     */
    WFUserList: function (callback) {
      var postData = {};
      UserInfoRequest.requestWFUserList(postData, function (response) {
        if (callback) {
          callback(response.status == 'ok', response.data);

          // ユーザー一覧をセット
          UserInfoManager.setData(Ext.decode(response.data));
        }
      });
    },

    /**
     * getUserInfoForAdmin
     *
     * @param page
     * @param callback
     */
    getUserInfoForAdmin: function (page, callback) {
      var postData = {
        page: page
      };

      UserInfoRequest.requestUserInfoAdmin(postData, function (response) {
        callback(response)
      });
    },

    /**
     * getInfoByEmail
     *
     * @param email
     * @returns {object}
     */
    getInfoByEmail: function (email) {
      return UserInfoManager.dataRaw.find(function (item, index) {
        return item.email == email;
      });
    },

    // METHOD:: Setter

    /**
     * initInfo
     *
     * @param callback
     */
    initInfo: function (callback) {
      var postData = {};
      UserInfoRequest.requestInitInfoUser(postData, function (response) {
        if (callback) {
          callback(response.status == 'ok')
        }
      });
    },

    /**
     * Set data to store
     *
     * @param {Array} data
     */
    setData: function (data) {
      UserInfoManager.dataRaw = data;
      if (UserInfoManager.store) {
        UserInfoManager.store.loadData(data);
      }
    },

  };
  UserInfoManager._init();

  /**
   * ユーザー情報インポートウィンドウ
   */
  UserImportWindow = {

    /**
     * showWindow
     *
     * ユーザーインポートウィンドウを表示する
     */
    showWindow: function () {
      // 読込中メッセージを表示
      SateraitoUI.showLoadingMessage();

      WorkflowUserManager.getToken(function (token) {

        // 読込中メッセージを消去
        SateraitoUI.clearMessage();

        var url = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/csvimport/userimport'
        url += '?hl=' + SATERAITO_LANG + '&token=' + token;

        var vHtml = '';
        vHtml += '<iframe src="' + url + '" style="width:99%;height:98%;">';
        vHtml += '</iframe>';

        var formPanel = {
          xtype: 'panel',
          autoWidth: true,
          autoScroll: false,
          border: false,
          html: vHtml
        };

        var buttons = [];
        buttons.push({
          iconCls: 'mdi mdi-close',
          text: MyLang.getMsg('MSG_CLOSE'),
          handler: function () {
            Ext.getCmp('user_import_window').close();
          }
        });

        // 詳細ウィンドウ
        var detailWindow = new Ext.Window({
          id: 'user_import_window',
          width: DisplayMgr.adjustByViewportWidth(545),
          height: DisplayMgr.adjustByViewportHeight(400),
          modal: true,
          bodyStyle: 'background-color:white;',
          title: MyLang.getMsg('MSG_INPUT_CSV_FILE'),
          plain: true,
          autoScroll: false,
          layout: 'fit',
          items: [formPanel],
          buttons: buttons
        });

        // ウィンドウを開く
        detailWindow.show();
      });
    }
  };

  /**
	 * ユーザーおよびグループを選択するウィンドウ
	 *
	 * GoogleAppsのAPIよりユーザー一覧およびグループ一覧をほぼリアルタイムで取得し、表示
	 */
	UserAndGroupSelectWindow = {

		/**
		 * createDataStore
		 *
		 * @return {Ext.data.ArrayStore}
		 */
		createDataStore: function()
		{
			return new Ext.data.ArrayStore({
				fields: [
					{name: 'email'},
					{name: 'user_name'}
				]
			});
		},

		/**
		 * createGrid
		 *
		 * ユーザー・グループ一覧グリッド
		 *
		 * @param {string} aTemplateBodyId
		 * @param {string} aElementNameToSet
		 */
		createGrid: function(callback)
		{
			var dataStore = UserAndGroupSelectWindow.createDataStore();
			var cols = [];

			cols.push({
				id: 'email',
				header: MyLang.getMsg('MSG_HEADER_EMAIL'),
				width: 170,
				dataIndex: 'email'
			});
			cols.push({
				id: 'user_name',
				header: MyLang.getMsg('MSG_USER_NAME'),
				width: 170,
				dataIndex: 'user_name'
			});

			// var cm = new Ext.grid.ColumnModel({
			var cm = Ext.grid.ColumnModel({
				items: ExtMixins.convertColumns(cols),
				defaults: {
					menuDisabled: true,
					sortable: true
				}
			});
			ExtMixins.destroyById('user_and_group_select_grid')
			return ({
				xtype: 'grid',
				id: 'user_and_group_select_grid',
				bodyStyle: 'background-color:white;',
				// cm: cm,
				columns: cm,
				store: dataStore,
				plain: true,
				stripeRows: true,
				selModel: {
					selType: 'rowmodel',
					mode: 'MULTI'
				},
				listeners: {
					keydown: function(e){
						if (e.getKey() == e.ENTER) {
							// Enterキーが押された場合、選択を実行
							if(typeof (callback) =='function'){
								UserAndGroupSelectWindow.getSelectClick(callback)
							}
						}
					},
					rowdblclick: function(grid, row, e)
					{
						// 行がダブルクリックされた場合、選択を実行
						if(typeof (callback) =='function'){
							UserAndGroupSelectWindow.getSelectClick(callback)
						}
					}
				}
			});
		},

		getSelectClick:function(callback){
			var grid = Ext.getCmp('user_and_group_select_grid');
      var data = [];
      
			// var records = sm.getSelections();
			var records = grid.getSelection();
			// 選択されたユーザーを承認者に追加
			if (records.length > 0) {
				Ext.each(records, function(record){
					if (typeof(record) != 'undefined') {
						// 選択されたユーザーのメールアドレス
						data.push({
              email: record.get('email'),
              user_name: record.get('user_name'),
            })
					}
				});
      }
      
      // callback for event on select user info in window
      callback(data);

			// ウィンドウを閉じる
			Ext.getCmp('user_select_window').close();

		},

		/**
		 * showByKeyword
		 *
		 * キーワードでサーチ
		 * 複数キーワードが入力されている場合、AND検索する
		 */
		showByKeyword: function(MyDataRecord, userStore, searchTextArray)
		{
			var nullToZeroStr = function(aParam){
				if (aParam == null) {
					return '';
				}
				return aParam;
			};

			// 検索結果の数を保持するカウンター
			var cntResult = 0;

			// step1. ユーザー検索
			Ext.each(AppsUser.userList, function(){
				var userEmail = nullToZeroStr(this.user_email);
				var userEmailLower = userEmail.toLowerCase();
				var userName = nullToZeroStr(this.family_name) + nullToZeroStr(this.given_name);
				var userNameLower = userName.toLowerCase();

				// スペースで区切られた全てのキーワードを含むかどうかチェック（AND検索）
				var containsAll = true;
				Ext.each(searchTextArray, function(){
					var searchText = ('' + this).trim();
					if (searchText != '') {
						if (userEmailLower.indexOf(searchText) != -1 || userNameLower.indexOf(searchText) != -1) {
							// キーワードにマッチした
							// no operation
						} else {
							// キーワードにマッチしなかった
							containsAll = false;
						}
					}
				});

				if (containsAll) {
					// 複数入力されたキーワードが、すべてマッチした場合
					// カウントアップして、件数チェック
					cntResult++;
					if (cntResult > Constants.MAX_SEARCH_RESULT) {
						SateraitoUI.MessageBox({
							icon: Ext.MessageBox.INFO,
							msg: MyLang.getMsg('MSG_MAX_ROW_100'),
							fn: function(){
							}
						});
						return false;
					}

					var newRecord = new MyDataRecord({
						email: userEmail,
						user_name: userName
					});
					userStore.add(newRecord);
				}
			});

			// 既に検索結果が100を超えている場合、ここで終了
			if (cntResult > Constants.MAX_SEARCH_RESULT) {
				return;
			}

			// step2. グループ検索
			Ext.each(AppsGroup.groupList, function(){
				var userEmail = nullToZeroStr(this.group_id);
				var userEmailLower = userEmail.toLowerCase();
				var userName = nullToZeroStr(this.group_name);
				var userNameLower = userName.toLowerCase();

				// スペースで区切られた全てのキーワードを含むかどうかチェック（AND検索）
				var containsAll = true;
				Ext.each(searchTextArray, function(){
					var searchText = '' + this;
					if (searchText != '') {
						if (userEmailLower.indexOf(searchText) != -1 || userNameLower.indexOf(searchText) != -1) {
							// キーワードにマッチした
							// no operation
						} else {
							// キーワードにマッチしなかった
							containsAll = false;
						}
					}
				});

				if (containsAll) {
					// 複数入力されたキーワードが、すべてマッチした場合
					// カウントアップして、件数チェック
					cntResult++;
					if (cntResult > Constants.MAX_SEARCH_RESULT) {
						SateraitoUI.MessageBox({
							icon: Ext.MessageBox.INFO,
							msg: MyLang.getMsg('MSG_MAX_ROW_100'),
							fn: function(){
							}
						});
						return false;
					}

					var newRecord = new MyDataRecord({
						email: userEmail,
						user_name: userName
					});
					userStore.add(newRecord);
				}
			});
		},

		/**
		 * showAll
		 *
		 * 全件表示
		 */
		showAll: function(MyDataRecord, userStore)
		{
			// 検索結果の数を保持するカウンター
			var cntResult = 0;
			// step1. ユーザー検索
			Ext.each(AppsUser.userList, function(){
				// カウントアップして、件数チェック
				cntResult++;
				if (cntResult > Constants.MAX_SEARCH_RESULT) {
					SateraitoUI.MessageBox({
						icon: Ext.MessageBox.INFO,
						msg: MyLang.getMsg('MSG_MAX_ROW_100'),
						fn: function(){
						}
					});
					return false;
				}

				var userEmail = '' + this.user_email;
				var userName = '' + this.family_name + this.given_name;
				var newRecord = new MyDataRecord({
					email: userEmail,
					user_name: userName
				});
				userStore.add(newRecord);
			});

			// step2. グループ検索
			Ext.each(AppsGroup.groupList, function(){
				// カウントアップして、件数チェック
				cntResult++;
				if (cntResult > Constants.MAX_SEARCH_RESULT) {
					SateraitoUI.MessageBox({
						icon: Ext.MessageBox.INFO,
						msg: MyLang.getMsg('MSG_MAX_ROW_100'),
						fn: function(){
						}
					});
					return false;
				}

				var userEmail = '' + this.group_id;
				var userName = '' + this.group_name;
				var newRecord = new MyDataRecord({
					email: userEmail,
					user_name: userName
				});
				userStore.add(newRecord);
			});
		},

		/**
		 * onSearchClick
		 *
		 * 「検索」ボタンをクリックしたときキックされる
		 */
		onSearchClick: function()
		{
			var userStore = Ext.getCmp('user_and_group_select_grid').getStore();
			userStore.removeAll();
			
			var MyDataRecord = userStore.model;

			var searchTextAll = Ext.getCmp('user_and_group_select_search_keyword').getValue();
			searchTextAll = searchTextAll.trim().toLowerCase();

			if (searchTextAll == '') {
				// 検索ボックスに入力値がない場合、全件表示する
				UserAndGroupSelectWindow.showAll(MyDataRecord, userStore);
			} else {
				// 通常検索
				var searchTextArray = searchTextAll.split(' ');
				UserAndGroupSelectWindow.showByKeyword(MyDataRecord, userStore, searchTextArray);
			}
		},

		/**
		 * showWindow
		 *
		 * ユーザー・グループ検索用ウィンドウを表示する
		 *
		 * @param {string} aTemplateBodyId
		 * @param {string} aElementNameToSet
		 */
		showWindow: function(callback)
		{
			// 既に表示されていたら、前面に出す
			var existingWindow = Ext.getCmp('user_select_window');
			if (!(typeof(existingWindow) == 'undefined' || existingWindow == null)) {
				existingWindow.toFront();
				return;
			}
			// 読込中メッセージを表示
			SateraitoUI.showLoadingMessage();
			// ユーザー一覧をロード
			AppsUser.requestUserList(function(){
				// グループ一覧をサーバーメモリー上にロード
				AppsGroup.requestGroupList(function(){
					// 読込中メッセージを消去
					SateraitoUI.clearMessage();

					var grid = UserAndGroupSelectWindow.createGrid(callback);
					var buttons = [];
					// 選択ボタン
					buttons.push({
            xtype: 'button',
            iconCls: 'mdi mdi-check',
						text: MyLang.getMsg('SELECT'),
						handler: function()
						{
							if(typeof (callback) == 'function'){
								UserAndGroupSelectWindow.getSelectClick(callback)
							}
						}
					});
					// キャンセルボタン
					buttons.push({
            xtype: 'button',
            iconCls: 'mdi mdi-close',
						text: MyLang.getMsg('CANCEL'),
						handler: function(){
							Ext.getCmp('user_select_window').close();
						}
					});
					// 検索語入力ボックス
					var inputBox = {
            xtype: 'textfield',
            width: '100%',
						id: 'user_and_group_select_search_keyword',
						listeners: {
							specialkey: function(f, e){
								if (e.getKey() == e.ENTER) {
									// Enterキーが押された場合、検索実行
									UserAndGroupSelectWindow.onSearchClick();
								} else if (e.getKey() == e.DOWN) {
									// 下キーが押された場合、グリッドにフォーカスを移動し、一番目の行を選択状態にする
									var grid = Ext.getCmp('user_and_group_select_grid');
									// grid.getSelectionModel().selectFirstRow();
									// grid.getView().focusRow(0);
									var store = grid.getStore();
									var firstRecord = store.getAt(0);
									if (firstRecord) {
										grid.getSelectionModel().select(firstRecord);
										(function(){
											grid.focus();
										}).defer(10);  // deferをかけないとグリッドにフォーカスが移ってから下キーが処理されてグリッドがスクロールする
									}
								}
							}
						}
					};
					var searchButton = {
						xtype: 'button',
						text: MyLang.getMsg("TXT_SEARCH"),
						handler: UserAndGroupSelectWindow.onSearchClick
					};

					inputBox.region = 'center';
					searchButton.region = 'east';

					var searchPanel = {
						xtype: 'panel',
            height: 35,
            layout: 'table',
            region: 'north',
            items: [inputBox, searchButton]
					};

					searchPanel.region = 'north';
					grid.region = 'center';

					var detailWindow = new Ext.Window({
						id: 'user_select_window',
						width: 400,
						height: 300,
						title: MyLang.getMsg("INFO_CIRCULATOR_SELECT"),
						plain: true,
						autoScroll: false,
						layout: 'border',
						//modal: true,
						items: [searchPanel, grid],
						buttons: buttons,
            listeners: {
              close: function () {
                callback([]);
              }
            }
					});
					// ウィンドウを表示
					detailWindow.show();
					// キーワード入力ボックスにカーソルをセット
					(function(){
						Ext.getCmp('user_and_group_select_search_keyword').focus();
					}).defer(500);
				});
			});
		}
	};


  /**
   * 組織アドレス帳連携用ポップアップ
   */
  KozukasanPopup = {
    /**
     * sateraitoShowPopup
     *
     * 組織アドレス帳ポップアップを表示する
     *
     * @param {callback} callback ... 組織アドレス帳選択が終わった時にキックされるコールバック
     *
     * ※この関数を使うには、グローバルスコープにRELATED_SATERAITO_ADDRESS_DOMAIN('https://sateraito-apps-address.appspot.com')が宣言されている必要があります
     */
    sateraitoShowPopup: function (callback) {

      var newWindow;

      function subSetAddress(e) {
        var data;
        newWindow.close();

        if (e.origin === RELATED_SATERAITO_ADDRESS_DOMAIN) {

          var addressString = e.data;	// "東京支店" <tokyo-div@shift-table.net>,"経営管理部" <tokyo-hr@shift-table.net>
          var addressStringSplited = addressString.split(',');	// "東京支店" <tokyo-div@shift-table.net>
          if (addressStringSplited.length == 0) {
            callback([]);
            return;
          }

          var data = [];
          Ext.each(addressStringSplited, function () {
            var entry = ('' + this).trim();		// "東京支店" <tokyo-div@shift-table.net>

            // メール抽出
            var emailToAdd;
            var re = new RegExp('<(.*)>');
            var matchResult = entry.match(re);
            if (matchResult) {
              emailToAdd = matchResult[1];
            }
            if (emailToAdd) {
              emailToAdd = emailToAdd.toLowerCase();
            }

            // 名前抽出
            var userName;
            var re2 = new RegExp('"(.*)"');
            var matchResult2 = entry.match(re2);
            if (matchResult2) {
              userName = matchResult2[1];
            }
            // 選択されたユーザーのメールアドレス
            var nameToAdd = '' + userName;

            // Push data width callback
            data.push({
              email: emailToAdd,
              user_name: nameToAdd
            });
          });
          callback(data);
        }
      }

      // sateraitoShowPopup2 関数の本体
      var scriptType,
        strCookie,
        strTitle;

      scriptType = 'document_kanri';
      strCookie = document.cookie;
      strTitle = MyLang.getMsg('MSG_SATERAITO_ADDRESS_BOOK');

      var vHtml = '';
      vHtml += '<html>';
      vHtml += '<head>';
      vHtml += '<title>' + strTitle + '</title>';
      vHtml += '</head>';
      vHtml += '<body style="margin:0px;padding:0px;">';
      vHtml += '<iframe src="' + RELATED_SATERAITO_ADDRESS_DOMAIN + '/' + MyUtil.getViewEmailDomainPart() + '/' + scriptType;
      vHtml += '/shared_contact.html?' + OtherSetting.sateraitoAddressPopupUrlParam + '" style="width:100%;height:99%;margin:0px;padding:0px;border: 1px solid #b5b8c8;">';
      vHtml += '</body>';
      vHtml += '</html>';
      newWindow = window.open('', '_blank', 'width=800px height=500px location=no status=no');

      var d = newWindow.document;
      d.open();
      d.write(vHtml);
      d.close();

      $(newWindow).on("beforeunload", function () {
        callback([]);
      })

      if (window.addEventListener) {
        // IE以外
        newWindow.addEventListener('message', subSetAddress, false);
      } else if (window.attachEvent) {
        // IE8
        newWindow.attachEvent('onmessage', subSetAddress);
      }
    },

    /**
     * sateraitoShowPopup2
     *
     * 組織アドレス帳ポップアップを表示する
     *
     * @param {string} aReceiveElementId ... 組織アドレス帳からの選択結果を流し込むエレメントのIDを指定
     * @param {function} callback ... 組織アドレス帳選択が終わった時にキックされるコールバック
     *
     * ※この関数を使うには、グローバルスコープにRELATED_SATERAITO_ADDRESS_DOMAIN('https://sateraito-apps-address.appspot.com')が宣言されている必要があります
     */
    sateraitoShowPopup2: function (aReceiveElementId, callback) {

      var newWindow;

      function setEmail(strMail) {
        var elmInput;
        elmInput = document.getElementById(aReceiveElementId);
        if (elmInput) {
          if (elmInput.value === '') {
            elmInput.value = strMail;
          } else {
            elmInput.value += ',' + strMail;
          }
          callback();
        }
      }

      function subSetAddress(e) {
        var data;
        newWindow.close();

        // console.log('message received origin=' + e.origin);
        if (e.origin === RELATED_SATERAITO_ADDRESS_DOMAIN) {
          setEmail(e.data);
        }
      }

      // sateraitoShowPopup2 関数の本体
      var scriptType,
        strCookie,
        strTitle;

      scriptType = 'document_kanri';
      strCookie = document.cookie;
      if (strCookie.indexOf('lang=en') >= 0) {
        strTitle = 'Sateraito Office - Group Address Book';
      } else {
        strTitle = 'サテライトオフィス・組織アドレス帳';
      }

      var vHtml = '';
      vHtml += '<html>';
      vHtml += '<head>';
      vHtml += '<title>' + strTitle + '</title>';
      vHtml += '</head>';
      vHtml += '<body style="margin:0px;padding:0px;overflow:hidden">';
      vHtml += '<iframe src="' + RELATED_SATERAITO_ADDRESS_DOMAIN + '/' + MyUtil.getViewEmailDomainPart() + '/' + scriptType;
      vHtml += '/shared_contact.html?' + OtherSetting.sateraitoAddressPopupUrlParam + '" style="width:100%;height:99%;margin:0px;padding:0px;">';
      vHtml += '</body>';
      vHtml += '</html>';
      newWindow = window.open('', '_blank', 'width=800px height=500px location=no status=no');

      var d = newWindow.document;
      d.open();
      d.write(vHtml);
      d.close();

      if (window.addEventListener) {
        // IE以外
        newWindow.addEventListener('message', subSetAddress, false);
      } else if (window.attachEvent) {
        // IE8
        newWindow.attachEvent('onmessage', subSetAddress);
      }
    }
  };

  /**
   * ファイルのダウンロード用ハンドラ
   */
  DownloadHandler = {

    /**
     * bindDownloadAttachedFileLink
     *
     * ダウンロードリンクのイベントハンドラをバインドする
     * span.download_attached_fileとa.download_attached_fileの２種類がある
     * クリック時にトークンを取得して非同期にダウンロードする場合は良いが、
     * クリック時にトークンを取得して非同期にポップアップでPDFを表示しようとすると、ブラウザーのポップアップブロックに引っかかるため、
     *
     * この関数は「ガジェットを開いたタイミングで」コールされる
     */
    bindDownloadAttachedFileLink: function () {

      var handlerDownload = function (element, token) {
        // ダウンロードリンククリック時のイベント
        var typeItem = $(element).attr('type_item');
        var deletedFlag = $(element).attr('deleted_flag');

        if (Sateraito.Util.strToBool(deletedFlag)) {
          return;
        }

        if (typeItem == Constants.TYPE_FILE) {
          DownloadHandler.goDownload(token, element, 'downloadattachedfile');
        } else if (typeItem == Constants.TYPE_ATTACH_EMAIL) {
          ManagerImportPlugin.onDownloadFile(element);
        }
      };


      $(document).on('click', '.download_attached_file', function () {
        var element = this;

        if (LoginMgr.token) {
          handlerDownload(element, LoginMgr.token);
        } else {
          WorkflowUserManager.getToken(function (token) {
            LoginMgr.token = token;
            handlerDownload(element, LoginMgr.token)
          });
        }
      });
    },

    /**
     * bindDownloadAttachedFileLinkAdmin
     *
     * ダウンロードリンクのイベントハンドラをバインドする（アドミン画面用）
     */
    bindDownloadAttachedFileLinkAdmin: function () {
      // // 先にトークンを取得してクリックイベントのなかでコールバックを起こさない（ポップアップがブロックされるため）
      var handlerDownload = function (element, token) {
        // ダウンロードリンククリック時のイベント
        var typeItem = $(element).attr('type_item');
        var deletedFlag = $(element).attr('deleted_flag');
        var mimeType = $(element).attr('mime_type');

        if (mimeType == Constants.TYPE_FOLDER) {
          return;
        }

        DownloadHandler.goDownload(token, element, 'downloadattachedfileadmin');
      };

      $(document).on('click', '.download_attached_file_admin', function () {
        var element = this;

        if (LoginMgr.token) {
          handlerDownload(element, LoginMgr.token);

        } else {
          WorkflowUserManager.getToken(function (token) {
            LoginMgr.token = token;
            handlerDownload(element, LoginMgr.token)
          });
        }
      });
    },

    /**
     * goDownload
     *
     * ダウンロード実行
     *
     * @param {string} token
     * @param {object} element
     */
    goDownload: function (token, element, aDownloader) {
      var fileId = $(element).attr('file_id');

      // pdfかどうかを判別
      var isPdf = false;
      if ($(element).attr('is_pdf') == '1') {
        isPdf = true;
      }

      // ダウンロードOKかどうか
      if ($(element).attr('downloadable') != '1') {
        if (FolderSelectedWindow.dailogCmp && LocalSettingsManager.settings.folderSelected.layout == 'list') {
          FolderSelectedWindow.dailogCmp.hide();
        }
        Ext.Msg.show({
          icon: Ext.MessageBox.ERROR,
          msg: MyLang.getMsg('HAVE_NO_PRIV_TO_DOWNLOAD'),
          buttons: Ext.Msg.OK,
          fn: function (buttonId) {
            if (FolderSelectedWindow.dailogCmp && LocalSettingsManager.settings.folderSelected.layout == 'list') {
              FolderSelectedWindow.dailogCmp.show();
            }
          }
        });
        return;
      }

      var downloadUrl = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/attach/' + aDownloader;
      downloadUrl += '?file_id=' + encodeURIComponent(fileId)
      downloadUrl += '&token=' + encodeURIComponent(token)
      downloadUrl += '&screen=' + encodeURIComponent(LoginMgr.screenName);
      downloadUrl += '&inline=' + encodeURIComponent(false);

      var grid = CreateWorkflowDocPanel.gridFileUploaded;

      if ($('#dummy_frame').size() == 0) {
        $('body').append('<iframe id="dummy_frame"></iframe>');
      }
      if (isPdf) {
        window.open(downloadUrl + '&inline=1');
      } else {
        $('#dummy_frame').attr('src', downloadUrl);
      }
    },

    /**
     * requestIsFilePdf
     *
     * ファイルがPDFかどうかチェックするリクエスト
     *
     * @param {string} aFileId ... ファイルID
     * @param {Function} callback
     */
    requestIsFilePdf: function (aFileId, callback) {
      if (IS_OPENID_MODE) {
        DownloadHandler._requestIsFilePdfOid(aFileId, callback);
      } else {
        DownloadHandler._requestIsFilePdf(aFileId, callback);
      }
    },

    /**
     * _requestIsFilePdf
     *
     * ファイルがPDFかどうかチェックするリクエスト(ガジェットIO版)
     *
     * @param {string} aFileId
     * @param {Function} callback
     * @param {number} aNumRetry
     */
    _requestIsFilePdf: function (aFileId, callback, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      var url = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/attach/getisfilepdf?file_id=' + encodeURIComponent(aFileId);
      gadgets.io.makeRequest(url, function (response) {

        if (!response.data) {

          // response error
          var err = response.errors[0];
          Sateraito.Util.console(err);

          SateraitoUI.showTimerMessage(MyLang.getMsg('RELOADING') + ' ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
            DownloadHandler._requestIsFilePdf(aFileId, callback, (aNumRetry + 1));
          } else {
            // １０回リトライしたがだめだった
            // メッセージは出さない
          }

          return;
        }

        var jsondata = response.data;

        // コールバックをキック
        callback(jsondata);

      }, Sateraito.Util.requestParam());
    },

    /**
     * _requestIsFilePdfOid
     *
     * ファイルがPDFかどうかチェックするリクエスト(OpenID版)
     *
     * @param {string} aFileId
     * @param {Function} callback
     * @param {number} aNumRetry
     */
    _requestIsFilePdfOid: function (aFileId, callback, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }
      // リクエスト
      Ext.Ajax.request({
        url: SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/attach/oid/getisfilepdf?file_id=' + encodeURIComponent(aFileId),
        success: function (response, options) {
          var jsondata = Ext.decode(response.responseText);

          // コールバックをキック
          callback(jsondata);
        },
        failure: function () {
          // 失敗時
          Sateraito.Util.console('retrying ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {

            // リトライ
            DownloadHandler._requestIsFilePdfOid(aFileId, callback, (aNumRetry + 1));

          } else {

            // １０回リトライしたがだめだった
          }
        }
      });
    }
  };

  /**
   * LocalSettingsManager
   *
   */
  LocalSettingsManager = {

    settings: {
      gridWorkflowDocColumnsWidth: {
      },
      gridMyWorkflowDocColumnsWidth: {
      },
      gridWorkflowDocSharedWithMeColumnsWidth: {
      },
      folderSelected: {
        layout: 'grid',
      }
    },

    _init: function () {
      LocalSettingsManager.loadAllLocalSettings(LocalSettingsManager.settings, true);
    },

    loadLocalSetting: function (key) {
      if (!Storage) {
        return;
      }

      if (key != undefined) {
        var key_prefix = SATERAITO_GOOGLE_APPS_DOMAIN + '__' + APP_ID + '__';
        return localStorage.getItem(key_prefix + key);
      }
    },

    loadAllLocalSettings: function (dictDefault, isOverwrite) {
      var key_prefix = SATERAITO_GOOGLE_APPS_DOMAIN + '__' + APP_ID + '__';

      var dictResult = {};
      for (var key in dictDefault) {
        var oldValue = dictDefault[key];
        var newValue = LocalStrageManager.get(key_prefix + key);

        if (newValue) {
          var value = newValue;
          if (typeof oldValue === 'number') {
            value = parseFloat(newValue);
          } else if (typeof oldValue === 'boolean') {
            if (newValue.toLowerCase() == 'true') {
              value = true;
            } else {
              value = false;
            }
          } else {
            if (typeof oldValue === 'object') {
              value = JSON.parse(newValue);
            }
          }

          dictResult[key] = value;

          if (isOverwrite) {
            dictDefault[key] = value;
          }
        } else {
          dictResult[key] = oldValue;
        }
      }

      return dictResult;
    },

    saveLocalSetting: function (key, value) {
      if (key != undefined && value != undefined) {
        if (typeof value == 'number') {
          value = value.toString();
        } else if (typeof value === 'object') {
          value = JSON.stringify(value);
        }

        var key_prefix = SATERAITO_GOOGLE_APPS_DOMAIN + '__' + APP_ID + '__';
        LocalStrageManager.set(key_prefix + key, value);
      }
    },

    setSettingGridWorkflowDocColumnSize: function (key, value) {
      LocalSettingsManager.settings.gridWorkflowDocColumnsWidth[key] = value;
      LocalSettingsManager.saveLocalSetting("gridWorkflowDocColumnsWidth", LocalSettingsManager.settings.gridWorkflowDocColumnsWidth);
    },

    setSettingGridMyWorkflowDocColumnSize: function (key, value) {
      LocalSettingsManager.settings.gridMyWorkflowDocColumnsWidth[key] = value;
      LocalSettingsManager.saveLocalSetting("gridMyWorkflowDocColumnsWidth", LocalSettingsManager.settings.gridMyWorkflowDocColumnsWidth);
    },

    setSettingGridWorkflowDocSharedWithMeColumnSize: function (key, value) {
      LocalSettingsManager.settings.gridWorkflowDocSharedWithMeColumnsWidth[key] = value;
      LocalSettingsManager.saveLocalSetting("gridWorkflowDocSharedWithMeColumnsWidth", LocalSettingsManager.settings.gridWorkflowDocSharedWithMeColumnsWidth);
    },

    setSettingLayoutShowFolder: function (key, value) {
      LocalSettingsManager.settings.folderSelected[key] = value;
      LocalSettingsManager.saveLocalSetting("folderSelected", LocalSettingsManager.settings.folderSelected);
    },
  }
  try {
    if (localStorage) {
      LocalSettingsManager._init();
    }
  } catch (e) { }

  /**
   * DocFolderImportWindow
   *
   */
  DocFolderImportWindow = {

    dialogImport: null,

    /**
     * showWindow
     *
     */
    showWindow: function (callback) {
      // 読込中メッセージを表示
      SateraitoUI.showLoadingMessage();

      WorkflowUserManager.getToken(function (token) {

        // 読込中メッセージを消去
        SateraitoUI.clearMessage();

        var url = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/csvimport/docfolderimport'
        url += '?hl=' + SATERAITO_LANG + '&token=' + token;

        var vHtml = '';
        vHtml += '<iframe src="' + url + '" style="width:99%;height:98%;">';
        vHtml += '</iframe>';

        var formPanel = {
          xtype: 'panel',
          autoWidth: true,
          autoScroll: false,
          border: false,
          html: vHtml
        };

        var buttons = [];
        buttons.push({
          iconCls: 'mdi mdi-close',
          text: MyLang.getMsg('MSG_CLOSE'),
          handler: function () {
            DocFolderImportWindow.dialogImport.close();
          }
        });

        // 詳細ウィンドウ
        DocFolderImportWindow.dialogImport = Ext.create({
          xtype: 'window',
          id: 'doc_folder_import_window',
          width: DisplayMgr.adjustByViewportWidth(800),
          height: DisplayMgr.adjustByViewportHeight(500),
          modal: true,
          bodyStyle: 'background-color:white;',
          title: MyLang.getMsg('MSG_INPUT_CSV_FILE'),
          plain: true,
          autoScroll: false,
          layout: 'fit',
          items: [formPanel],
          buttons: buttons,
          listeners: {
            close: function () {
              DocFolderImportWindow.dialogImport = null;

              if (typeof callback == 'function') {
                callback();
              }
            }
          }
        });

        // ウィンドウを開く
        DocFolderImportWindow.dialogImport.show();
      });
    }
  };

  /**
   * WorkflowDocImportWindow
   *
   */
  WorkflowDocImportWindow = {

    dialogImport: null,

    /**
     * showWindow
     *
     */
    showWindow: function (callback) {
      // 読込中メッセージを表示
      SateraitoUI.showLoadingMessage();

      WorkflowUserManager.getToken(function (token) {

        // 読込中メッセージを消去
        SateraitoUI.clearMessage();

        var url = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/csvimport/workflowdocimport'
        url += '?hl=' + SATERAITO_LANG + '&token=' + token;

        var vHtml = '';
        vHtml += '<iframe src="' + url + '" style="width:99%;height:98%;">';
        vHtml += '</iframe>';

        var formPanel = {
          xtype: 'panel',
          autoWidth: true,
          autoScroll: false,
          border: false,
          html: vHtml
        };

        var buttons = [];
        buttons.push({
          iconCls: 'mdi mdi-close',
          text: MyLang.getMsg('MSG_CLOSE'),
          handler: function () {
            WorkflowDocImportWindow.dialogImport.close();
          }
        });

        // 詳細ウィンドウ
        WorkflowDocImportWindow.dialogImport = Ext.create({
          xtype: 'window',
          id: 'workflow_doc_import_window',
          width: DisplayMgr.adjustByViewportWidth(800),
          height: DisplayMgr.adjustByViewportHeight(500),
          modal: true,
          bodyStyle: 'background-color:white;',
          title: MyLang.getMsg('MSG_INPUT_CSV_FILE'),
          plain: true,
          autoScroll: false,
          layout: 'fit',
          items: [formPanel],
          buttons: buttons,
          listeners: {
            close: function () {
              WorkflowDocImportWindow.dialogImport = null;

              if (typeof callback == 'function') {
                callback();
              }
            }
          }
        });

        // ウィンドウを開く
        WorkflowDocImportWindow.dialogImport.show();
      });
    }
  };

  /**
   * DocFolderManager
   *
   */
  DocFolderManager = {
    store: null,
    dataRaw: [],

    _init: function () {
      DocFolderManager.store = DocFolderManager.createDataStore();
    },

    // METHOD:: Create

    /**
     * createDataStore
     *
     * ドキュメントのためのデータストアを作成
     *
     * @return {Object}
     */
    createDataStore: function () {
      var store = new Ext.data.ArrayStore({
        autoDestroy: true,
        storeId: 'docfolder_store',
        fields: [
          {name: 'folder_code'},
          {name: 'folder_name'},
        ]
      });

      store.setData(DocFolderManager.dataRaw)

      return store;
    },

    // METHOD:: Setter

    /**
     * Call request update a folder
     *
     * @param {object} postData
     * @param {callback} callback
     * @param {boolean} aIsAdminMode
     */
    update: function (postData, callback, aIsAdminMode) {
      DocFolderRequest.update(postData, function (aJsondata) {
        if (typeof (callback) == 'function') {
          callback(aJsondata.status == 'ok', aJsondata.folder, aJsondata.error_code);
        }
      }, aIsAdminMode);
    },

    move: function (listIdFolderMove, moveToFolderId, callback, aIsAdminMode) {
      var postData = {
        'list_id_folder_move': listIdFolderMove.join(Constants.KEY_SPLIT_RAW),
        'key_split_raw': Constants.KEY_SPLIT_RAW,
        'to_folder_id': moveToFolderId,
        'lang': MyLang.getLocale(),
      };

      DocFolderRequest.move(postData, function (aJsondata) {
        if (typeof (callback) == 'function') {
          callback(aJsondata.status == 'ok', aJsondata.error_code);
        }
      }, aIsAdminMode);
    },

    copy: function (listIdFolderCopy, copyToFolderId, callback, aIsAdminMode) {
      var postData = {
        'list_id_folder_copy': listIdFolderCopy.join(Constants.KEY_SPLIT_RAW),
        'key_split_raw': Constants.KEY_SPLIT_RAW,
        'to_folder_id': copyToFolderId,
        'lang': MyLang.getLocale(),
      };

      DocFolderRequest.copy(postData, function (aJsondata) {
        if (typeof (callback) == 'function') {
          callback(aJsondata.status == 'ok', aJsondata.folders, aJsondata.error_code);
        }
      }, aIsAdminMode);
    },

    delete: function (folderCode, callback, aIsAdminMode) {
      var postData = {
        screen: LoginMgr.screenName,
        'list_id_folder': folderCode.join(Constants.KEY_SPLIT_RAW),
        'key_split_raw': Constants.KEY_SPLIT_RAW,
        'lang': MyLang.getLocale(),
      };

      DocFolderRequest.delete(postData, function (aJsondata) {
        if (typeof (callback) == 'function') {
          callback(aJsondata.status == 'ok', aJsondata.error_code);
        }
      }, aIsAdminMode);
    },

    /**
     * Remove all data in store
     *
     */
    removeAllData: function () {
      DocFolderManager.store.removeAll();
    },

    /**
     * Set data to store
     *
     * @param {Array} data
     */
    setData: function (data) {
      DocFolderManager.dataRaw = data;
      if (DocFolderManager.store) {
        DocFolderManager.store.loadData(data);
      }
    },

    /**
     * Send request load data folder
     *
     * @param {callback} callback
     */
    loadData: function (callback) {
      if (MyPanel.nameScreen == Constants.SCREEN_ADMIN_CONSOLE) {
        DocFolderRequest.getAllByAdmin({}, function (success, data) {
          if (success) {
            DocFolderManager.setData(data)
          }

          if (typeof (callback) == 'function') {
            callback(success)
          }
        });
      } else {
        DocFolderRequest.getAll({}, function (success, data) {
          if (success) {
            DocFolderManager.setData(data)
          }

          if (typeof (callback) == 'function') {
            callback(success)
          }
        });
      }
    },

    // METHOD:: Getter
    checkUserCanUpload: function (folderCode, callback, aIsAdminMode) {
      if (typeof(aIsAdminMode) == 'undefined') {
        aIsAdminMode = false;
      }

      DocFolderRequest.requestCheckFolderUserCanUpload(folderCode, function (aJsondata) {
        if (typeof (callback) == 'function') {
          callback(aJsondata.status == 'ok', aJsondata.error_code);
        }
      }, aIsAdminMode);
    },

    checkUserSubfolderCreatable: function (folderCode, callback, aIsAdminMode) {
      if (typeof (aIsAdminMode) == 'undefined') {
        aIsAdminMode = false;
      }

      DocFolderRequest.requestCheckUserSubfolderCreatable(folderCode, function (aJsondata) {
        if (typeof (callback) == 'function') {
          callback(aJsondata.status == 'ok', aJsondata.error_code);
        }
      }, aIsAdminMode);
    },

    getFullpathPathName: function (folderCode, callback, aIsAdminMode) {
      if (typeof(aIsAdminMode) == 'undefined') {
        aIsAdminMode = false;
      }

      DocFolderRequest.requestGetFolderNameFullpathPath(folderCode, function (aJsondata) {
        if (typeof (callback) == 'function') {
          callback(aJsondata.status == 'ok', aJsondata.folder_name_fullpath, aJsondata.msg_error);
        }
      }, aIsAdminMode);
    },

    getFullpathPathNameByAdmin: function (folderCode, callback, aIsAdminMode) {
      if (typeof(aIsAdminMode) == 'undefined') {
        aIsAdminMode = false;
      }

      DocFolderRequest.requestGetFolderNameFullpathPathByAdmin(folderCode, function (aJsondata) {
        if (typeof (callback) == 'function') {
          callback(aJsondata.status == 'ok', aJsondata.folder_name_fullpath, aJsondata.msg_error);
        }
      }, aIsAdminMode);
    },

    totalFileSize: function (callback) {
      DocFolderRequest.requestTotalFileSize(function (aJsondata) {
        if (typeof (callback) == 'function') {
          callback(aJsondata.status == 'ok', aJsondata.number);
        }
      });
    },

    maxTotalFileSize: function (callback) {
      DocFolderRequest.requestMaxTotalFileSize(function (aJsondata) {
        if (typeof (callback) == 'function') {
          callback(aJsondata.status == 'ok', aJsondata.number);
        }
      });
    },

    appIdTotalFileSize: function (callback) {
      DocFolderRequest.requestAppIdTotalFileSize(function (aJsondata) {
        if (typeof (callback) == 'function') {
          callback(aJsondata.status == 'ok', aJsondata.number);
        }
      });
    },

  };
  DocFolderManager._init();

  /**
   * GooglePickerAPI
   *
   */
  GooglePickerAPI = {
    accessToken: null,
    tokenClient: false,
    pickerInited: false,
    gisInited: false,
    pickerShow: null,

    /**
     * _init
     *
     * @private
     */
    _init: function () {
      gapi.load('picker');
    },

    /**
     * createPicker
     *
     * @param callback
     */
    createPicker: function (callback) {
      FileflowDocManager.getAccessTokenGGDrive(VIEWER_EMAIL, function (response) {
        GooglePickerAPI._createPicker(response.access_token, response.developer_key, callback);
      });
    },

    /**
     * _createPicker
     *
     * @param {string} accessToken
     * @param {string} developerKey
     * @param {callback} pickerCallback
     * @private
     */
    _createPicker: function (accessToken, developerKey, pickerCallback) {
      var origin = window.location.origin;
      // URLパラメータより設定を取得
      var urlParams = MyUtil.getUrlParams();

      if (urlParams['origin_parent']) {
        origin = urlParams['origin_parent'];
      } else {
        try {
          origin = window.parent.location.origin;
        } catch (err) {
          origin = 'https://sites.google.com';
        }
      }

      var view = new google.picker.View(google.picker.ViewId.DOCS);

      var docsView = new google.picker.DocsView()
          .setIncludeFolders(true)
          .setSelectFolderEnabled(true);

      var docsUploadView = new google.picker.DocsUploadView()
        .setIncludeFolders(true); // show folder for upload

      GooglePickerAPI.pickerShow = new google.picker.PickerBuilder()
        .setOAuthToken(accessToken)
        .setDeveloperKey(developerKey)
        .setOrigin(origin)

        .setCallback(function (response) {
          if (response.action == 'loaded') return;

          if (response.docs) {
            pickerCallback(response.action, response.docs, response.viewToken)
          }
        })

        .enableFeature(google.picker.Feature.MULTISELECT_ENABLED)
        .enableFeature(google.picker.Feature.SUPPORT_DRIVES)

        .addView(view)
        .addView(docsView)
        .addView(docsUploadView)

        .setLocale(MyLang.getLocale())

        .build();

      // Show picker
      GooglePickerAPI.pickerShow.setVisible(true);
    },
  };

  /**
   * DetailDocPopup
   *
   */
  DetailDocPopup = {
    isShowDetail: false,

    showPopupDetail: function (workflowDocId, keyFilterDocDeleted, option) {
      DetailDocPopup.isShowDetail = true;

      if (typeof (option) == 'undefined') {
        option = {};
      }
      var is_gadget_admin = LoginMgr.is_gadget_admin;
      if (typeof (is_gadget_admin) == 'undefined') {
        is_gadget_admin = false;
      }

      var url = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/docdetailpopup/' + workflowDocId
          url += '?token='+ LoginMgr.token
          url += '&hl=' + SATERAITO_LANG
          url += '&is_gadget_admin=' + is_gadget_admin;
          url += '&screen=' + MyPanel.nameScreen;
          url += '&key_filter_doc_deleted=' + keyFilterDocDeleted;
      // if (option.mode_backup) {
      //   url = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/docdetailpopup/backup/' + workflowDocId + '?hl=' + SATERAITO_LANG;
      // }

      var newWindow;

      /**
       * messageReceivedCallback
       *
       * 掲示板に投稿した場合のコールバック
       */
      var messageReceivedCallback = function (e) {
        //isPopup block action auto close popup when click keyword after install extension
        var data = typeof (e.data) === 'object' ? e.data : JSON.parse(e.data);
        var isPopup = data.is_popup;
        if (isPopup) {
          newWindow.close();
          if (data.message == 'reload_data') {
            FormSearchPanel.handlerClearForm();
          } else {
            console.log('message received origin=' + e.origin);
          }
        }
      };

      // showPopup 関数の本体
      var windowTitle = MyLang.getMsg('WINDOW_TITLE_DETAIL');

      var vHtml = '';
      vHtml += '<html>';
      vHtml += '<head>';
      vHtml += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />';

      vHtml += '<title>' + windowTitle + '</title>';
      vHtml += '</head>';
      vHtml += '<body style="margin:0;">';
      vHtml += '<iframe name="output_frame" src="' + url + '"';
      vHtml += '" style="width:100%;height:100%;margin:0px;padding:0px;border:none;">';
      vHtml += '</body>';
      vHtml += '</html>';
      newWindow = window.open('', '_blank', 'width=1050px height=550px location=no status=no resizable=yes');
      // newWindow = window.open();

      var d = newWindow.document;
      d.open();
      d.write(vHtml);
      d.close();

      if (window.addEventListener) {
        // IE以外
        newWindow.addEventListener('message', messageReceivedCallback, false);
      } else if (window.attachEvent) {
        // IE8
        newWindow.attachEvent('onmessage', messageReceivedCallback);
      }
    }
  };

  /**
   * MasterData
   *
   */
  MasterData = {

    dataStore: {},
    masterData: {},
    masterDef: {},

    /**
     * createDataStore
     *
     * @param {string} aMasterCode
     */
    createDataStore: function (aMasterCode) {
      return new Ext.data.ArrayStore({
        id: 'store_master_data_' + aMasterCode,
        fields: [
          {name: 'master_code'},
          {name: 'data_key'},
          {name: 'attribute_1'},
          {name: 'attribute_2'},
          {name: 'attribute_3'},
          {name: 'attribute_4'},
          {name: 'attribute_5'},
          {name: 'attribute_6'},
          {name: 'attribute_7'},
          {name: 'attribute_8'},
          {name: 'attribute_9'},
          {name: 'attribute_10'},
          {name: 'attribute_11'},
          {name: 'attribute_12'},
          {name: 'attribute_13'},
          {name: 'attribute_14'},
          {name: 'attribute_15'},
          {name: 'attribute_16'},
          {name: 'attribute_17'},
          {name: 'attribute_18'},
          {name: 'attribute_19'},
          {name: 'attribute_20'},
          {name: 'attribute_21'},
          {name: 'attribute_22'},
          {name: 'attribute_23'},
          {name: 'attribute_24'},
          {name: 'attribute_25'},
          {name: 'attribute_26'},
          {name: 'attribute_27'},
          {name: 'attribute_28'},
          {name: 'attribute_29'},
          {name: 'attribute_30'},
          {name: 'attribute_31'},
          {name: 'attribute_32'},
          {name: 'attribute_33'},
          {name: 'attribute_34'},
          {name: 'attribute_35'},
          {name: 'attribute_36'},
          {name: 'attribute_37'},
          {name: 'attribute_38'},
          {name: 'attribute_39'},
          {name: 'attribute_40'},
          {name: 'attribute_41'},
          {name: 'attribute_42'},
          {name: 'attribute_43'},
          {name: 'attribute_44'},
          {name: 'attribute_45'},
          {name: 'attribute_46'},
          {name: 'attribute_47'},
          {name: 'attribute_48'},
          {name: 'attribute_49'},
          {name: 'attribute_50'},
          {name: 'comment'},
          {name: 'created_date'}
        ]
      });
    },

    /**
     * hasMasterDataCache
     *
     * @param {string} aMasterCode
     * @return {boolean}
     */
    hasMasterDataCache: function (aMasterCode) {
      // キャッシュをチェック
      if (typeof (MasterData.masterData[aMasterCode]) != 'undefined') {
        // キャッシュがあった
        return true;
      }
      return false;
    },

    /**
     * putToDatastore
     *
     * @param {string} aMasterCode
     * @param {Array} aJsondata
     */
    putToDatastore: function (aMasterCode, aJsondata) {
      // データ追加
      var masterDatas = [];

      Ext.each(aJsondata, function () {
        masterDatas.push([
          this.master_code,
          this.data_key,
          this.attribute_1,
          this.attribute_2,
          this.attribute_3,
          this.attribute_4,
          this.attribute_5,
          this.attribute_6,
          this.attribute_7,
          this.attribute_8,
          this.attribute_9,
          this.attribute_10,
          this.attribute_11,
          this.attribute_12,
          this.attribute_13,
          this.attribute_14,
          this.attribute_15,
          this.attribute_16,
          this.attribute_17,
          this.attribute_18,
          this.attribute_19,
          this.attribute_20,
          this.attribute_21,
          this.attribute_22,
          this.attribute_23,
          this.attribute_24,
          this.attribute_25,
          this.attribute_26,
          this.attribute_27,
          this.attribute_28,
          this.attribute_29,
          this.attribute_30,
          this.attribute_31,
          this.attribute_32,
          this.attribute_33,
          this.attribute_34,
          this.attribute_35,
          this.attribute_36,
          this.attribute_37,
          this.attribute_38,
          this.attribute_39,
          this.attribute_40,
          this.attribute_41,
          this.attribute_42,
          this.attribute_43,
          this.attribute_44,
          this.attribute_45,
          this.attribute_46,
          this.attribute_47,
          this.attribute_48,
          this.attribute_49,
          this.attribute_50,
          this.comment
        ]);
      });

      // データストアにデータをロードし、グリッドに表示させる
      MasterData.dataStore[aMasterCode].loadData(masterDatas);
    },

    /**
     * requestDeleteMasterData
     *
     * @param {string} aMasterCode
     * @param {Function} callback
     */
    requestDeleteMasterData: function (aMasterCode, callback) {
      var postData = {
        master_code: aMasterCode
      };

      var baseUrl = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/master';
      var methodUrl = '/deletemaster';
      SimpleRequest.post({
        baseUrl: baseUrl,
        methodUrl: methodUrl,
        postData: postData,
        busyMsg: MyLang.getMsg('UPDATING'),
        callback: callback
      });
    },

    /**
     * requestUpdateMasterDef
     *
     * @param {string} aMasterCode
     * @param {callback} callback
     * @param {number} aNumRetry
     */
    requestUpdateMasterDef: function (aMasterCode, callback, aNumRetry) {
      var insertFlag = '0';
      if (aMasterCode == '__new_master') {
        insertFlag = '1';
      }

      var elMasterCode = $('#master_data_def_form_' + aMasterCode).find('input[name=\'master_code\']')[0];
      var elMasterName = $('#master_data_def_form_' + aMasterCode).find('input[name=\'master_name\']')[0];
      var elKeyName = $('#master_data_def_form_' + aMasterCode).find('input[name=\'data_key_name\']')[0];
      var elUseLTCache = $('#master_data_def_form_' + aMasterCode).find('input[name=\'is_use_ltcache\']')[0];

      // 送信用データを作成
      var postData = {
        'master_code': elMasterCode.value.trim(),
        'master_name': elMasterName.value.trim(),
        'data_key_name': elKeyName.value.trim(),
        'is_use_ltcache': elUseLTCache.checked,
        'insert_flag': insertFlag
      };

      // Validate value post
      var elError = null, keyMsgError = null;
      if (postData['master_code'] == '') {
        elError = elMasterCode;
        keyMsgError = 'MSG_ERROR_EMPTY_MASTER_CODE';
      } else if (postData['master_name'] == '') {
        elError = elMasterName;
        keyMsgError = 'MSG_ERROR_EMPTY_MASTER_NAME';
      } else if (postData['data_key_name'] == '') {
        elError = elKeyName;
        keyMsgError = 'MSG_ERROR_EMPTY_DATA_KEY_NAME';
      }
      if (elError != null) {
        Ext.Msg.show({
          icon: Ext.MessageBox.ERROR,
          msg: MyLang.getMsg(keyMsgError),
          buttons: Ext.Msg.OK,
          fn: function () {
            elError.focus();
            Ext.getCmp('save_master_def_button').enable();
          }
        });
        return;
      }

      for (var i = 1; i <= Constants.NUM_ATTRIBUTES_MASTER_DATA; i++) {
        postData['attribute_' + i + '_name'] = $('#master_data_def_form_' + aMasterCode).find('input[name=\'attribute_' + i + '_name\']').val()
      }

      var baseUrl = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/master';
      var methodUrl = '/updatemasterdef';
      SimpleRequest.post({
        baseUrl: baseUrl,
        methodUrl: methodUrl,
        postData: postData,
        busyMsg: MyLang.getMsg('UPDATING'),
        callback: callback
      });
    },

    /**
     * requestMasterData
     *
     * マスターデータの取得
     *
     * @param {string} aMasterCode
     * @param {boolean} aCacheOk
     * @param {boolean} aAdminMode
     * @param {Function} callback
     * @param {number} page
     */
    requestMasterData: function (aMasterCode, aCacheOk, aAdminMode, callback, page) {
      if (typeof (page) == 'undefined') {
        page = 1;
      }
      if (IS_OPENID_MODE) {
        // OpenIDモードの場合
        MasterData._requestMasterDataOid(aMasterCode, aCacheOk, aAdminMode, callback, page);
      } else if (IS_TOKEN_MODE) {
        MasterData._requestMasterDataToken(aMasterCode, aCacheOk, aAdminMode, callback, page);
      } else if (IS_PUBLIC_ANYONE) {
        MasterData._requestMasterDataPublic(aMasterCode, aCacheOk, aAdminMode, callback, page);
      } else {
        MasterData._requestMasterData(aMasterCode, aCacheOk, aAdminMode, callback, page);
      }
    },

    /**
     * _requestMasterData
     *
     * マスターデータの取得（ガジェットIO版）
     *
     * @param {string} aMasterCode
     * @param {boolean} aCacheOk
     * @param {boolean} aAdminMode
     * @param {Function} callback
     * @param {number} page
     * @param {number} aNumRetry
     */
    _requestMasterData: function (aMasterCode, aCacheOk, aAdminMode, callback, page, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      // キャッシュOKの場合
      if (aCacheOk) {
        // キャッシュをチェック
        if (typeof (MasterData.masterData[aMasterCode]) != 'undefined') {
          // キャッシュがあった
          callback(MasterData.masterData[aMasterCode]);
          return;
        }
      }

      // 読込中メッセージを表示
      SateraitoUI.showLoadingMessage();

      var pageName = 'getmasterdata';
      if (aAdminMode) {
        pageName = 'getmasterdataadmin';
      }

      var url = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/master/' + pageName + '?master_code=' + encodeURIComponent(aMasterCode) + '&page=' + page;
      gadgets.io.makeRequest(url, function (response) {

        if (!response.data) {

          // response error
          var err = response.errors[0];
          Sateraito.Util.console(err);

          SateraitoUI.showTimerMessage(MyLang.getMsg('RELOADING') + ' ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
            // リトライ
            MasterData._requestMasterData(aMasterCode, aCacheOk, aAdminMode, callback, page, (aNumRetry + 1));
          } else {
            // エラーメッセージ
            if (response.rc == 401) {
              SateraitoUI.showLoadingMessage(MyLang.getMsg('ERROR_TIMEOUT'));
            } else {
              SateraitoUI.showTimerMessage(MyLang.getMsg('ERROR_WHILE_LOADING'), 10);
            }
          }

          return;
        }

        var jsondata = response.data;

        // キャッシュに保存
        MasterData.masterData[aMasterCode] = jsondata;

        // 読込中メッセージを消去
        SateraitoUI.clearMessage();

        // コールバックをキック
        callback(jsondata);
      }, Sateraito.Util.requestParam());
    },

    /**
     * _requestMasterDataOid
     *
     * マスターデータの取得（OpenID版）
     *
     * @param {string} aMasterCode
     * @param {boolean} aCacheOk
     * @param {boolean} aAdminMode
     * @param {Function} callback
     * @param {number} page
     * @param {number} aNumRetry
     */
    _requestMasterDataOid: function (aMasterCode, aCacheOk, aAdminMode, callback, page, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      // キャッシュOKの場合
      if (aCacheOk) {
        // キャッシュをチェック
        if (typeof (MasterData.masterData[aMasterCode]) != 'undefined') {
          // キャッシュがあった
          callback(MasterData.masterData[aMasterCode]);
          return;
        }
      }

      // 読込中メッセージを表示
      SateraitoUI.showLoadingMessage();

      var pageName = 'getmasterdata';
      if (aAdminMode) {
        pageName = 'getmasterdataadmin';
      }

      // リクエスト
      var url = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/master/oid/' + pageName + '?master_code=' + encodeURIComponent(aMasterCode) + '&page=' + page;
      Ext.Ajax.request({
        url: url,
        success: function (response, options) {
          var jsondata = Ext.decode(response.responseText);
          // キャッシュに保存
          MasterData.masterData[aMasterCode] = jsondata;
          // 読込中メッセージを消去
          SateraitoUI.clearMessage();
          // コールバックをキック
          callback(jsondata);
        },
        failure: function () {
          // 失敗時
          Sateraito.Util.console(MyLang.getMsg('RETRYING') + aNumRetry);
          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
            // リトライ
            MasterData._requestMasterDataOid(aMasterCode, aCacheOk, aAdminMode, callback, page, (aNumRetry + 1));
          } else {
            // １０回リトライしたがだめだった
            // 読込中メッセージを消去
            SateraitoUI.clearMessage();
          }
        }
      });
    },

    /**
     * _requestMasterDataToken
     *
     * @param {string} aMasterCode
     * @param {boolean} aCacheOk
     * @param {boolean} aAdminMode
     * @param {callback} callback
     * @param {number} page
     * @param {number} aNumRetry
     * @private
     */
    _requestMasterDataToken: function (aMasterCode, aCacheOk, aAdminMode, callback, page, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      // キャッシュOKの場合
      if (aCacheOk) {
        // キャッシュをチェック
        if (typeof (MasterData.masterData[aMasterCode]) != 'undefined') {
          // キャッシュがあった
          callback(MasterData.masterData[aMasterCode]);
          return;
        }
      }

      // 読込中メッセージを表示
      SateraitoUI.showLoadingMessage();

      var pageName = 'getmasterdata';
      if (aAdminMode) {
        pageName = 'getmasterdataadmin';
      }

      // リクエスト
      var url = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/master/token/' + pageName + '?token=' + USER_TOKEN + '&master_code=' + encodeURIComponent(aMasterCode) + '&page=' + page;
      Ext.Ajax.request({
        url: url,
        success: function (response, options) {
          var jsondata = Ext.decode(response.responseText);
          // キャッシュに保存
          MasterData.masterData[aMasterCode] = jsondata;
          // 読込中メッセージを消去
          SateraitoUI.clearMessage();
          // コールバックをキック
          callback(jsondata);
        },
        failure: function () {
          // 失敗時
          Sateraito.Util.console(MyLang.getMsg('RETRYING') + aNumRetry);
          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
            // リトライ
            MasterData._requestMasterDataToken(aMasterCode, aCacheOk, aAdminMode, callback, page, (aNumRetry + 1));
          } else {
            // １０回リトライしたがだめだった
            // 読込中メッセージを消去
            SateraitoUI.clearMessage();
          }
        }
      });
    },

    /**
     * _requestMasterDataPublic
     *
     * @param {string} aMasterCode
     * @param {boolean} aCacheOk
     * @param {boolean} aAdminMode
     * @param {callback} callback
     * @param {number} page
     * @param {number} aNumRetry
     * @private
     */
    _requestMasterDataPublic: function (aMasterCode, aCacheOk, aAdminMode, callback, page, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      // キャッシュOKの場合
      if (aCacheOk) {
        // キャッシュをチェック
        if (typeof (MasterData.masterData[aMasterCode]) != 'undefined') {
          // キャッシュがあった
          callback(MasterData.masterData[aMasterCode]);
          return;
        }
      }

      // 読込中メッセージを表示
      SateraitoUI.showLoadingMessage();

      var pageName = 'getmasterdata';
      if (aAdminMode) {
        pageName = 'getmasterdataadmin';
      }

      // リクエスト
      var url = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/master/public/' + pageName + '?master_code=' + encodeURIComponent(aMasterCode) + '&page=' + page;
      Ext.Ajax.request({
        url: url,
        success: function (response, options) {
          var jsondata = Ext.decode(response.responseText);
          // キャッシュに保存
          MasterData.masterData[aMasterCode] = jsondata;
          // 読込中メッセージを消去
          SateraitoUI.clearMessage();
          // コールバックをキック
          callback(jsondata);
        },
        failure: function () {
          // 失敗時
          Sateraito.Util.console(MyLang.getMsg('RETRYING') + aNumRetry);
          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
            // リトライ
            MasterData._requestMasterDataPublic(aMasterCode, aCacheOk, aAdminMode, callback, page, (aNumRetry + 1));
          } else {
            // １０回リトライしたがだめだった
            // 読込中メッセージを消去
            SateraitoUI.clearMessage();
          }
        }
      });
    },

    /**
     * requestMasterDataRow
     *
     * @param {string} aMasterCode
     * @param {string} aDataKeyValue
     * @param {function} callback
     * @param {number} aNumRetry
     */
    requestMasterDataRow: function (aMasterCode, aDataKeyValue, callback, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }
      if (IS_OPENID_MODE) {
        MasterData._requestMasterDataRowOid(aMasterCode, aDataKeyValue, callback, aNumRetry);
      } else if (IS_TOKEN_MODE) {
        MasterData._requestMasterDataRowToken(aMasterCode, aDataKeyValue, callback, aNumRetry);
      } else if (IS_PUBLIC_ANYONE) {
        MasterData._requestMasterDataRowPublic(aMasterCode, aDataKeyValue, callback, aNumRetry);
      } else {
        MasterData._requestMasterDataRow(aMasterCode, aDataKeyValue, callback, aNumRetry);
      }
    },

    /**
     * _requestMasterDataRow
     *
     * ガジェットIO版
     *
     * @param {string} aMasterCode
     * @param {string} aDataKeyValue
     * @param {Function} callback
     * @param {number} aNumRetry
     */
    _requestMasterDataRow: function (aMasterCode, aDataKeyValue, callback, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      // 読込中メッセージを表示
      SateraitoUI.showLoadingMessage();

      var url = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/master/getmasterdatarow?master_code=' + encodeURIComponent(aMasterCode) + '&data_key=' + encodeURIComponent(aDataKeyValue);
      gadgets.io.makeRequest(url, function (response) {

        if (!response.data) {

          // response error
          var err = response.errors[0];
          Sateraito.Util.console(err);

          SateraitoUI.showTimerMessage(MyLang.getMsg('RELOADING') + ' ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
            // リトライ
            MasterData._requestMasterDataRow(aMasterCode, aDataKeyValue, callback, (aNumRetry + 1));
          } else {
            // エラーメッセージ
            if (response.rc == 401) {
              SateraitoUI.showLoadingMessage(MyLang.getMsg('ERROR_TIMEOUT'));
            } else {
              SateraitoUI.showTimerMessage(MyLang.getMsg('ERROR_WHILE_LOADING'), 10);
            }
          }
          return;
        }

        var jsondata = response.data;
        // 読込中メッセージを消去
        SateraitoUI.clearMessage();
        // コールバックをキック
        callback(jsondata);
      }, Sateraito.Util.requestParam());
    },

    /**
     * _requestMasterDataRowOid
     *
     * OpenID版
     *
     * @param {string} aMasterCode
     * @param {string} aDataKeyValue
     * @param {function} callback
     * @param {number} aNumRetry
     */
    _requestMasterDataRowOid: function (aMasterCode, aDataKeyValue, callback, aNumRetry) {
      // 読込中メッセージを表示
      //if (!DisplayMgr.isLoadMaskShown()) {
      SateraitoUI.showLoadingMessage();
      //}

      // 送信データ作成
      var postData = {
        data_key: aDataKeyValue,
        master_code: aMasterCode
      };

      // リクエスト
      Ext.Ajax.request({
        url: SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/master/oid/getmasterdatarow',
        params: postData,
        success: function (response, options) {
          // 読込中メッセージを消去
          SateraitoUI.clearMessage();

          var jsondata = Ext.decode(response.responseText);
          callback(jsondata);
        },
        failure: function () {
          SateraitoUI.showTimerMessage(MyLang.getMsg('RELOADING') + ' ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
            // リトライ
            MasterData._requestMasterDataRowOid(aMasterCode, aDataKeyValue, callback, (aNumRetry + 1));
          } else {
            // １０回リトライしたがだめだった
            SateraitoUI.showTimerMessage(MyLang.getMsg('ERROR_WHILE_LOADING'), 10);
          }
        }
      });
    },

    /**
     * _requestMasterDataRowToken
     *
     * @param {string} aMasterCode
     * @param {string} aDataKeyValue
     * @param {callback} callback
     * @param {number} aNumRetry
     * @private
     */
    _requestMasterDataRowToken: function (aMasterCode, aDataKeyValue, callback, aNumRetry) {
      // 読込中メッセージを表示
      //if (!DisplayMgr.isLoadMaskShown()) {
      SateraitoUI.showLoadingMessage();
      //}

      // 送信データ作成
      var postData = {
        data_key: aDataKeyValue,
        master_code: aMasterCode,
        token: USER_TOKEN
      };

      // リクエスト
      Ext.Ajax.request({
        url: SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/master/token/getmasterdatarow',
        params: postData,
        success: function (response, options) {
          // 読込中メッセージを消去
          SateraitoUI.clearMessage();

          var jsondata = Ext.decode(response.responseText);
          callback(jsondata);
        },
        failure: function () {
          SateraitoUI.showTimerMessage(MyLang.getMsg('RELOADING') + ' ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
            // リトライ
            MasterData._requestMasterDataRowToken(aMasterCode, aDataKeyValue, callback, (aNumRetry + 1));
          } else {
            // １０回リトライしたがだめだった
            SateraitoUI.showTimerMessage(MyLang.getMsg('ERROR_WHILE_LOADING'), 10);
          }
        }
      });
    },

    /**
     * _requestMasterDataRowPublic
     *
     * @param {string} aMasterCode
     * @param {string} aDataKeyValue
     * @param {callback} callback
     * @param {number} aNumRetry
     * @private
     */
    _requestMasterDataRowPublic: function (aMasterCode, aDataKeyValue, callback, aNumRetry) {
      // 読込中メッセージを表示
      //if (!DisplayMgr.isLoadMaskShown()) {
      SateraitoUI.showLoadingMessage();
      //}

      // 送信データ作成
      var postData = {
        data_key: aDataKeyValue,
        master_code: aMasterCode
      };

      // リクエスト
      Ext.Ajax.request({
        url: SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/master/public/getmasterdatarow',
        params: postData,
        success: function (response, options) {
          // 読込中メッセージを消去
          SateraitoUI.clearMessage();

          var jsondata = Ext.decode(response.responseText);
          callback(jsondata);
        },
        failure: function () {
          SateraitoUI.showTimerMessage(MyLang.getMsg('RELOADING') + ' ' + aNumRetry);

          if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
            // リトライ
            MasterData._requestMasterDataRowPublic(aMasterCode, aDataKeyValue, callback, (aNumRetry + 1));
          } else {
            // １０回リトライしたがだめだった
            SateraitoUI.showTimerMessage(MyLang.getMsg('ERROR_WHILE_LOADING'), 10);
          }
        }
      });
    },

    /**
     * requestMasterDef
     *
     * @param {string} aMasterCode
     * @param {boolean} aCacheOk
     * @param {Function} callback
     * @param {number} aNumRetry
     */
    requestMasterDef: function (aMasterCode, aCacheOk, callback, aNumRetry) {
      // キャッシュOKの場合、最新のデータは取りに行かない
      if (aCacheOk) {
        if (typeof (MasterData.masterDef[aMasterCode]) != 'undefined') {
          callback(MasterData.masterDef[aMasterCode]);
          return;
        }
      }

      var baseUrl = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/master';
      var methodUrl = '/getmasterdef?master_code=' + encodeURIComponent(aMasterCode);
      SimpleRequest.get({
        baseUrl: baseUrl,
        methodUrl: methodUrl,
        callback: function (jsondata) {
          if (jsondata.status == 'ng') {
            callback(null);
          } else {
            MasterData.masterDef[aMasterCode] = jsondata;
            if (typeof (callback) == 'function') {
              callback(jsondata);
            }
          }
        }
      });
    },

    /**
     * requestMasterDefList
     *
     * @param {Function} callback
     * @param {number} aNumRetry
     */
    requestMasterDefList: function (callback, aNumRetry) {
      var baseUrl = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/master';
      var methodUrl = '/getmasterlist';
      SimpleRequest.get({
        baseUrl: baseUrl,
        methodUrl: methodUrl,
        callback: callback
      });
    },
  };

  /**
   * フルテキスト検索用ウィンドウ
   */
  FulltextSearchWindow = {

    _searchedWords: null,
    rawValue: '',


    /**
     * checkFulltextReady
     *
     * ログイン中のユーザーにとってフルテキスト検索の準備が整っているかどうかチェック
     * フルテキスト検索用準備が整っていない場合、4秒からスタートするだんだん間隔が広がるポーリングを準備がととのうまでおこなう
     *
     * @param {Function} callback フルテキスト検索環境が整っている場合、キックされる
     * @param {number} aNumRetry
     */
    checkFulltextReady: function (callback, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      var baseUrl = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/textsearch';
      var methodUrl = '/checkfulltextready';

      SimpleRequest.get({
        baseUrl: baseUrl,
        methodUrl: methodUrl,
        enableRetry: true,
        callback: function (jsondata) {
          if (!jsondata.is_ready) {
            // まだフルテキスト検索がOKでない場合、(リトライ回数)秒後に再チェック
            var deferTime = aNumRetry * 1000;
            if (deferTime > 5000) {
              // 最大間隔5秒とする
              deferTime = 5000;
            }
            (function () {
              FulltextSearchWindow.checkFulltextReady(callback, (aNumRetry + 1));
            }).defer(deferTime);

          } else {
            // フルテキスト検索がOKになったら、コールバックをキック
            if (typeof (callback) == 'function') {
              var haveRechecked = aNumRetry > 1;

              callback(haveRechecked);
            }
          }
        }
      });
    },

    /**
     * requestFulltextSearch
     *
     * ドキュメントのフルテキスト検索を実行
     *
     * @param {string} aKeyword
     * @param {string} colSortValue
     * @param {string} typeSortValue
     * @param {number} aPage
     * @param {Function} callback
     */
    requestFulltextSearch: function (aKeyword, colSortValue, typeSortValue, aPage, callback) {
      var baseUrl = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/textsearch';
      var methodUrl = '/fulltextsearch';
      methodUrl += '?keyword=' + encodeURIComponent(aKeyword);
      methodUrl += '&page=' + aPage;
      methodUrl += '&grouping_direction=desc';		// debug
      methodUrl += '&category_col_sort=' + colSortValue;		// debug
      methodUrl += '&category_type_sort=' + typeSortValue;		// debug

      FulltextSearchWindow._requestFulltextSearch(aKeyword, aPage, baseUrl, methodUrl, callback);
    },

    /**
     * requestFulltextSearchAdmin
     *
     * ドキュメントのフルテキスト検索を実行
     *
     * @param {string} aKeyword
     * @param {number} aPage
     * @param {Function} callback
     */
    requestFulltextSearchAdmin: function (aKeyword, aPage, callback) {
      var baseUrl = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/textsearch';
      var methodUrl = '/fulltextsearchadmin';
      vUrl += '?keyword=' + encodeURIComponent(aKeyword);
      vUrl += '&page=' + aPage;

      FulltextSearchWindow._requestFulltextSearch(aKeyword, aPage, baseUrl, methodUrl, callback);
    },

    /**
     * _requestFulltextSearch
     *
     * ドキュメントのフルテキスト検索を実行
     *
     * @param {string} aKeyword
     * @param {number} aPage
     * @param {string} aUrl
     * @param {Function} callback
     * @param {number} aNumRetry
     */
    _requestFulltextSearch: function (aKeyword, aPage, baseUrl, methodUrl, callback, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      // 検索中メッセージを表示
      SateraitoUI.showLoadingMessage(MyLang.getMsg('SEARCHING'));

      SimpleRequest.get({
        baseUrl: baseUrl,
        methodUrl: methodUrl,
        enableRetry: true,
        callback: function (jsondata) {
          if (jsondata.status == 'ng') {
            // エラーの場合でも無内容でコールバックをキック
            callback({
              results: [],
              have_more_rows: false
            });
          } else {
            // コールバックをキック
            if (typeof (callback) == 'function') {
              callback(jsondata);
            }
          }
        }
      });
    },

    /**
     * requestSearchedWords
     *
     * 過去の検索語一覧を取得
     * ローカルキャッシュがある場合、それを返す
     *
     * @param {Function} callback
     * @param {number} aNumRetry
     */
    requestSearchedWords: function (callback, aNumRetry) {
      if (typeof (aNumRetry) == 'undefined') {
        aNumRetry = 1;
      }

      // ローカルキャッシュがある場合、それを返しておしまい
      if (FulltextSearchWindow._searchedWords != null) {
        callback(FulltextSearchWindow._searchedWords);
        return;
      }

      // 読込中メッセージを表示
      SateraitoUI.showLoadingMessageCnt();

      var baseUrl = SATERAITO_MY_SITE_URL + '/' + SATERAITO_GOOGLE_APPS_DOMAIN + '/' + LoginMgr.appId + '/textsearch';
      var methodUrl = '/getsearchedwords';

      SimpleRequest.get({
        baseUrl: baseUrl,
        methodUrl: methodUrl,
        enableRetry: true,
        callback: function (jsondata) {
          // ローカルキャッシュに保存
          FulltextSearchWindow._searchedWords = jsondata;

          // コールバックをキック
          if (typeof (callback) == 'function') {
            callback(jsondata);
          }
        }
      });
    },

    /**
     * createSearchInputBox
     *
     * 全文検索用テキストボックスを生成
     *
     * @param {Array} aSearchedWords ... 過去に検索したキーワード
     * @param {Function} callbackEnterKey
     * @param {boolean} aTypeAhead ... 入力時に候補を出すかどうか
     */
    createSearchInputBox: function (aSearchedWords, callbackEnterKey, aTypeAhead) {
      if (typeof (aTypeAhead) == 'undefined') {
        aTypeAhead = true;
      }

      var MAX_LENGTH = 50;

      return {
        xtype: 'combo',
        id: 'fulltext_search_keyword',
        height: 30,
        maxLength: MAX_LENGTH,
        autoCreate: {tag: 'input', type: 'text', size: '20', autocomlete: 'off', maxlength: '' + MAX_LENGTH},
        store: aSearchedWords,
        typeAhead: aTypeAhead,
        mode: 'local',
        triggerAction: 'all',
        emptyText: MyLang.getMsg('INPUT_KEYWORD'),
        selectOnFocus: true,
        hideTrigger: true,
        editable: true,
        forceSelection: false,
        listeners: {
          specialkey: function (field, e) {
            if (e.getKey() == e.ENTER) {
              if (FulltextSearchWindow.beforeselectFired) {
                Ext.getCmp('fulltext_search_keyword').setRawValue(FulltextSearchWindow.rawValue);
              }
              callbackEnterKey();
              return;
            }
          },
          beforeselect: function (combo, record, index) {
            var rawValue = Ext.getCmp('fulltext_search_keyword').getRawValue();
            var selectValue = record.json[0];
            FulltextSearchWindow.rawValue = rawValue;
            FulltextSearchWindow.beforeselectFired = true;
            (function () {
              FulltextSearchWindow.beforeselectFired = false;
            }).defer(10);
          },
          /**
           * Enterを押したとき、beforeselect --> select --> specialkey、と一気に発火するため、rawValueに入力値が入った状態で検索が実行される
           * beforeselectが発火しない場合もあり
           */
          select: function (combo, record, index) {
            (function () {
              var rawValue = Ext.getCmp('fulltext_search_keyword').getRawValue();
              FulltextSearchWindow.rawValue = rawValue;
            }).defer(10);
          }
        }
      };
    }
  };
})();

