(function(){
	
	Sateraito = {};
	
	Sateraito.GadgetHeight = {
		
		DEFAULT_GADGET_HEIGHT: 200,
		
		/**
		 * getUserPrefs
		 *
		 * @return {Number} ガジェット設定「gh」より読みだした「ガジェットの高さ」
		 */
		getUserPrefs: function(aDefaultRetVal)
		{
			var prefs = new gadgets.Prefs();
			var gadgetHeight = parseInt(prefs.getString('gh'), 10);
			if (isNaN(gadgetHeight)) {
				if (typeof(aDefaultRetVal) == 'undefined') {
					gadgetHeight = Sateraito.GadgetHeight.DEFAULT_GADGET_HEIGHT;
				} else {
					gadgetHeight = aDefaultRetVal;
				}
			}
			
			return gadgetHeight;
		},
		
		/**
		 * setGadgetHeight
		 *
		 * ガジェットの高さを再設定する
		 */
		setGadgetHeight: function(){
			(function(){
				if(gadgets && gadgets.window) {
          // gadgets.window.adjustHeight(Sateraito.GadgetHeight.getUserPrefs());
        }
			}).defer(1000);
		}
	};
	
	Sateraito.DateUtil = {
		
		dayOfWeek : ['日', '月', '火', '水', '木', '金', '土'],
		dayOfWeekEn : ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
		
		/**
		 * checkDate
		 *
		 * @param {Number} aYear
		 * @param {Number} aMonth
		 * @param {Number} aDay
		 */
		checkDate: function(aYear, aMonth, aDay) {
			var dt = new Date(aYear, aMonth - 1, aDay);
			if(dt == null || dt.getFullYear() != aYear || dt.getMonth() + 1 != aMonth || dt.getDate() != aDay) {
				return false;
			}
			return true;
		},
		
		/**
		 * datePart
		 *
		 * @param {string} aDateTimeStr YYYY-MM-DD HH:MI:SS形式の文字列
		 * @return {string} YYYY-MM-DD形式の文字列
		 */
		datePart: function (aDateTimeStr)
		{
			if (typeof(aDateTimeStr) == 'undefined') {
				return '';
			}
			var dateSplited = aDateTimeStr.split(' ');
			return dateSplited[0];
		},
		
		/**
		 * datetimeShorten
		 *
		 * @param {String} aTimeStr YYYY-MM-DD HH:MI:SS....形式
		 * @return {String} YYYY-MM-DD HH:MI形式
		 */
		datetimeShorten: function(aTimeStr)
		{
			if (typeof(aTimeStr) == 'undefined') {
				return '';
			}
			if (aTimeStr == '') {
				return '';
			}
			
			var timeStrSplited = aTimeStr.split(':');
			return timeStrSplited[0] + ':' + timeStrSplited[1];
		},
		
		/**
		 * formatNumToDate
		 *
		 * @param {Number} aYear
		 * @param {Number} aMonth
		 * @param {Number} aDay
		 */
		formatNumToDate: function(aYear, aMonth, aDay)
		{
			var strYear = '' + aYear;
			var strMonth = '';
			if (aMonth < 10) {
				strMonth = '0' + aMonth;
			} else {
				strMonth = '' + aMonth;
			}
			var strDay = '';
			if (aDay < 10) {
				strDay = '0' + aDay;
			} else {
				strDay = '' + aDay;
			}
			return strYear + '-' + strMonth + '-' + strDay;
		},
		
		/**
		 * getDateDiff
		 *
		 * @param {String} aDateSmall YYYY-MM-DD形式
		 * @param {String} aDateBig YYYY-MM-DD形式
		 */
		getDateDiff: function(aDateSmall, aDateBig)
		{
			// 開始日を日付オブジェクトに変換
			var dateSmallSplited = aDateSmall.split('-');
			var dateSmallObj = new Date(parseInt(dateSmallSplited[0], 10), parseInt(dateSmallSplited[1], 10) - 1, parseInt(dateSmallSplited[2], 10));
			// 終了日を日付オブジェクトに変換
			var dateBigSplited = aDateBig.split('-');
			var dateBigObj = new Date(parseInt(dateBigSplited[0], 10), parseInt(dateBigSplited[1], 10) - 1, parseInt(dateBigSplited[2], 10));
			var diff = dateBigObj - dateSmallObj;
			var diffDay = diff / (24 * 60 * 60 * 1000); // マイクロ秒 --> 何日間に変換
			return diffDay;
		},
		
		/**
		 * getFutureDateStr
		 *
		 * delta日後の日付文字列を取得
		 *
		 * @param {String} aDateStr YYYY-MM-DD形式の日付文字列
		 * @param {Number} aDelta 日付に足す日数
		 * @return {String} YYYY-MM-DD 形式の日付文字列
		 */
		getFutureDateStr: function(aDateStr, aDelta)
		{
			if (typeof(aDateStr) == 'undefined') {
				return null;
			}
			var dateStrSplited = aDateStr.split('-');
			var retDate = new Date(parseInt(dateStrSplited[0], 10), parseInt(dateStrSplited[1], 10) - 1, parseInt(dateStrSplited[2], 10));
			retDate.setTime(retDate.getTime() + aDelta * 24 * 60 * 60 * 1000);
			
			return Sateraito.DateUtil.myFormatDate(retDate);
		},
		
		/**
		 * getTodayStr
		 *
		 * @return {String} 本日の日付文字列(YYYY-MM-DD)
		 */	
		getTodayStr: function()
		{
			var today = new Date();
			return Sateraito.DateUtil.myFormatDate(today);
		},
		
		/**
		 * myFormatDate
		 *
		 * 日付オブジェクトよりゼロ付きのYYYY-MM-DD形式文字列を返す
		 *
		 * @param {Date} aDate 日付
		 * @return {String|null} YYYY-MM-DD形式文字列
		 */	
		myFormatDate: function(aDate)
		{
			var yearPart = aDate.getFullYear();
			var monthPart = aDate.getMonth() + 1;
			var dayPart = aDate.getDate();
			
			if (monthPart < 10) monthPart = '0' + monthPart;
			if (dayPart < 10) dayPart = '0' + dayPart;
			
			return '' + yearPart + '-' + monthPart + '-' + dayPart;
		},
		
		/**
		 * timeShorten
		 *
		 * @param {String} aTimeStr HH:MI:SS形式
		 * @return {String} HH:MI形式
		 */
		timeShorten: function(aTimeStr)
		{
			if (typeof(aTimeStr) == 'undefined') {
				return '';
			}
			if (aTimeStr == '') {
				return '';
			}
			
			var timeStrSplited = aTimeStr.split(':');
			return timeStrSplited[0] + ':' + timeStrSplited[1];
		},
		
		/**
		 * shorten
		 *
		 * @param {String} aDateStr YYYY-MM-DD形式
		 * @return {String} M/DD形式
		 */
		shorten: function(aDateStr)
		{
			var dateStrSplited = aDateStr.split('-');
			var vMonth = parseInt(dateStrSplited[1], 10);

			return '' + vMonth + '/' + dateStrSplited[2]
		}
	};
	
	Sateraito.Lang = {
		
		/**
		 * getMsg
		 *
		 * @param aMsgCd {String} メッセージコード
		 * @return {String} 国別メッセージ
		 */
		getMsg: function(aMsgCd)
		{
			var prefs = new gadgets.Prefs();
			return prefs.getMsg(aMsgCd);
		}
	};
	
	Sateraito.Util = {
		
		/**
		 * console
		 */
		console: function(aMsg)
		{
			if (typeof(window.console) != 'undefined') {
				window.console.log(aMsg);
			}
		},
		
		/**
		 * escapeHtml
		 *
		 * HTML制御文字列をエスケープする
		 *
		 * @param {String} aStringToEscape
		 */
		escapeHtml: function(aStringToEscape)
		{
			if (aStringToEscape == null) {
				return null;
			}
			if (typeof(aStringToEscape) != 'string') {
				return aStringToEscape;
			}
			return aStringToEscape.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
		},
		
		/**
		 * enterToBr
		 *
		 * @param {String} aStringToChange
		 */
		enterToBr: function(aStringToChange)
		{
			if (aStringToChange == null) {
				return '';
			}
			if (typeof(aStringToChange) == 'undefined') {
				return '';
			}
			return aStringToChange.replace(/\n/g, '<br />');
		},
		
		/**
		 * isAllSingleByteChar
		 *
		 * 文字列がすべて半角キャラクターかどうかチェック
		 * 半角カナを含んでいた場合もfalseを返す
		 *
		 * @param {string} aStrValue
		 * @return {boolean}
		 */
		isAllSingleByteChar: function(aStrValue)
		{
			for (var i = 0; i < aStrValue.length; i++) {
				var c = aStrValue.charAt(i);
				if (' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'.indexOf(c) >= 0){
					// c is single byte char
				} else {
					// c is double-byte char
					return false;
				}
			}
			return true;
		},
		
		/**
		 * isAllSplitedValEmail
		 *
		 * 文字列が、「demo1@examplc.com demo2@example.com」のように半角スペース区切りのメールアドレス列挙のフォーマットかどうかチェック
		 *
		 * @param {string} aStrValue
		 * @param {boolean} 全ての列挙されたものがメールアドレスの場合true
		 */
		isAllSplitedValEmail: function(aStrValue)
		{
			var strValueSplited = aStrValue.split(' ');
			var haveError = false;
			Ext.each(strValueSplited, function(aEachVal){
				if (Sateraito.Util.isMailAddress(aEachVal)) {
					// メールアドレスなのでOK
				} else {
					// メールアドレスでない
					haveError = true;
					return false;
				}
			});
			if (haveError) {
				return false;
			}
			return true;
		},
		
		/**
		 * isMailAddress
		 *
		 * 文字列がメールアドレスかどうかを判定
		 *
		 * @param {String} aStr
		 * @return {boolean} 文字列がメールアドレスの場合True
		 */
		isMailAddress: function(aStr)
		{
			if (aStr == null || typeof(aStr) == 'undefined') {
				return false;
			}
			
			var splitedByAtmark = aStr.split('@');
			if (splitedByAtmark.length != 2) {
				return false;
			}
			// var splitedByDot = splitedByAtmark[1].split('.');
			// if (splitedByDot.length < 2) {
			// 	return false;
			// }
			return true;
		},

		/**
		 * mailIncludeListDomain
		 *
		 * @param {String} email
		 * @return {boolean}
		 */
		mailIncludeListDomain: function(email)
		{
			if (!Sateraito.Util.isMailAddress(email)) {
				return false;
			}

			var domainEmail = email.split('@')[1];

			return LIST_GOOGLE_APPS_DOMAIN.includes(domainEmail);
		},
		
		/**
		* isSmartPhone
		*
		* スマートフォンかどうかを返す
		*
		* @param {boolean} true ... スマートフォンである
		*/
		isSmartPhone: function() {
			var strUseragent = window.navigator.userAgent;
			if (strUseragent.indexOf('iPhone' ) >= 0 ||
			    strUseragent.indexOf('iPad'   ) >= 0 ||
			    strUseragent.indexOf('iPod'   ) >= 0 ||
			    strUseragent.indexOf('Android') >= 0) {
				return true;
			} else {
				return false;
			}
		},
		
		/**
		 * myBoolToNum
		 *
		 * @param {boolean} aBooleanValue
		 * @return {Number}
		 */
		myBoolToNum: function(aBooleanValue)
		{
			if (aBooleanValue) {
				return 1;
			}
			return 0;
		},
		
		/**
		 * myImplode
		 *
		 * @param {Object} aArray 配列
		 * @param {string} aDelimiter 区切り文字、指定しない場合は「,」になる
		 * @return {string} カンマ区切りでデータを並べた文字列
		 */
		myImplode: function(aArray, aDelimiter)
		{
			if (typeof(aDelimiter) == 'undefined') {
				aDelimiter = ',';
			}
			
			var retVal = '';
			Ext.each(aArray, function(value, index){
				if (retVal != '') retVal += aDelimiter;
				retVal += value;
			});
			return retVal;
		},
		
		/**
		 * removeHtmlTag
		 *
		 * html文字列からhtmlタグを除去する
		 *
		 * special thanks to Tatsuya Blog
		 *
		 * @param {string} aStringToRemoveTag
		 */
		removeHtmlTag: function(aStringToRemoveTag)
		{
			if (aStringToRemoveTag == null) {
				return null;
			}
			if (typeof(aStringToRemoveTag) != 'string') {
				return aStringToRemoveTag;
			}
			var delExp = new RegExp('<\/?[^>]+>', 'gim');
			var replacedStr = aStringToRemoveTag.replace(delExp, '');
			return replacedStr;
		},
		
		/**
		 * requestParam
		 *
		 * gadget.io.makeRequest用のリクエストパラメータオブジェクトを作成する
		 *
		 * @param {boolean} aIsPost POSTリクエストにする場合はtrueをセットする
		 * @param {Object} aPostData POSTするデータ
		 * @param {number} aRefreshInterval ガジェットコンテナ側にキャッシュする秒数をセットする
		 *
		 * @return obj parameters to send by makeRequest
		 */
		requestParam: function(aIsPost, aPostData, aRefreshInterval)
		{
			if (typeof(aIsPost) == 'undefined') {
				aIsPost = false;
			}
			if (typeof(aRefreshInterval) == 'undefined') {
				aRefreshInterval = 0;
			}
			
			var param = {};
			param[gadgets.io.RequestParameters.CONTENT_TYPE] = gadgets.io.ContentType.JSON;
			param[gadgets.io.RequestParameters.AUTHORIZATION] = gadgets.io.AuthorizationType.SIGNED;
			param[gadgets.io.RequestParameters.REFRESH_INTERVAL] = aRefreshInterval;
			if (aIsPost) {
				param[gadgets.io.RequestParameters.METHOD] = gadgets.io.MethodType.POST;
				param[gadgets.io.RequestParameters.POST_DATA] = gadgets.io.encodeValues(aPostData);
			} else {
				param[gadgets.io.RequestParameters.METHOD] = gadgets.io.MethodType.GET;
			}
			return param;
		},
    /**
     * strRight
     *
     * 文字列の右側から指定文字数だけ切り出して返す
     *
     * @param {string} aStringToGetRightSubstring .. 切り出す元になる文字列
     * @param {number} aLength .. 切り出す文字数
     * @return {string}
     */
    strRight: function(aStringToGetRightSubstring, aLength)
    {
      return String(aStringToGetRightSubstring).substr(aLength * (-1));
    },

    /**
     * strLeft
     *
     * @param {string} aStringToGetLeftSubstring .. 切り出す元になる文字列
     * @param {number} aLength .. 切り出す文字数
     */
    strLeft: function(aStringToGetLeftSubstring, aLength)
    {
      return String(aStringToGetLeftSubstring).substr(0, aLength);
    },

    /**
     * strEndWith
     *
     * 文字列の末尾が指定文字列に一致すればtrueを返す
     *
     * @param {string} aStringToCheck
     * @param {string} aEndString
     * @return {boolean}
     */
    strEndWith: function(aStringToCheck, aEndString)
    {
      if (Sateraito.Util.strRight(aStringToCheck, aEndString.length) == aEndString) {
        return true;
      }
      return false;
    },

    /**
     * strStartWith
     *
     * 文字列の銭湯が指定文字列に一致すればtrueを返す
     *
     * @param {string} aStringToCheck
     * @param {string} aStartString
     * @return {boolean}
     */
    strStartWith: function(aStringToCheck, aStartString)
    {
      if (Sateraito.Util.strLeft(aStringToCheck, aStartString.length) == aStartString) {
        return true;
      }
      return false;
		},
		
		/**
		 * isSecurityBrowser
		 *
		 * セキュリティブラウザかどうかを返す
		 *
		 * @return {boolean} true ... セキュリティブラウザである
		 */
		isSecurityBrowser: function()
		{
			var strUseragent = window.navigator.userAgent;
			if (strUseragent.indexOf('SateraitoSecurityBrowser') >= 0) {
				return true;
			} else {
				return false;
			}
		},

		/**
		 * isIosSmartPhone
		 *
		 * 「iOSの」スマートフォンかどうかを返す
		 * 端末がAndroidの場合はfalseを返す
		 *
		 * @return {boolean}
		 */
		isIosSmartPhone: function () {
			var strUseragent = window.navigator.userAgent;
			if (strUseragent.indexOf('iPhone') >= 0 ||
				strUseragent.indexOf('iPad') >= 0 ||
				strUseragent.indexOf('iPod') >= 0) {
				return true;
			} else {
				return false;
			}
		},

		boolToStr: function(aBooleanValue)
		{
			if (aBooleanValue) {
				return 'true';
			}
			return 'false';
		},

		strToBool: function(aStrValue)
		{
			if (String(aStrValue).toLowerCase() == 'true' || String(aStrValue) == '1') {
				return true;
			}

			return false;
		},
	};

	Sateraito.MiniMessage = {
		
		message: null,
		fontSize: 12,
		
		/**
		 * initMessageArea
		 */
		initMessageArea: function(aFontSize)
		{
			var vHtml = '';
			vHtml += '<div id="mini_message" style="';
			if (typeof(aFontSize) == 'undefined') {
				// no option
			} else {
				Sateraito.MiniMessage.fontSize = aFontSize;
			}
			vHtml += '"></div>';
			
			// Add Mini Message Area
			$('body').append(vHtml);

			// メッセージの位置を再配置
			var bodyWidth = $(window).width();
			var messageAreaWidth = $('#mini_message').width();
			$('#mini_message').css('left', '' + ((bodyWidth / 2) - (messageAreaWidth / 2)) + 'px');
		},
		
		/**
		 * clearMessage
		 *
		 * メッセージを消去する
		 */
		clearMessage: function()
		{
      if (IS_OPENID_MODE) {
        _OidMiniMessage.clearMessage();
      } else {
        if (Sateraito.MiniMessage.message != null) {
          // メッセージを消す
          var prefs = new gadgets.Prefs();
          var msg = new gadgets.MiniMessage(prefs.getModuleId(), $('#mini_message')[0]);
          msg.dismissMessage(Sateraito.MiniMessage.message);
          Sateraito.MiniMessage.message = null;
        }
      }
		},
		
		/**
		 * showTimerMessage
		 *
		 * 時間がたつと消えるメッセージを表示
		 *
		 * @param {String} aMessageText
		 * @param {Number} aTime
		 */
		showTimerMessage: function(aMessageText, aTime)
		{
			if (IS_OPENID_MODE) {
        _OidMiniMessage.showTimerMessage(aMessageText, aTime);
      } else {
        if (typeof(aTime) == 'undefined') {
          aTime = 3;
        }
        var prefs = new gadgets.Prefs();
        var msg = new gadgets.MiniMessage(prefs.getModuleId(), $('#mini_message')[0]);
        var element = msg.createTimerMessage(aMessageText, aTime);
        element.style.fontSize = '' + Sateraito.MiniMessage.fontSize + 'px';
      }
		},
		
		/**
		 * showLoadingMessage
		 *
		 * @param {String} aMessageText 表示する読み込み中メッセージ（省略すると、デフォルトの読み込み中メッセージを表示）
		 */
		showLoadingMessage: function(aMessageText)
		{
      if (IS_OPENID_MODE) {
        _OidMiniMessage.showLoadingMessage(aMessageText);
      } else {
        var prefs = new gadgets.Prefs();

        Sateraito.MiniMessage.clearMessage();

        // 読込中メッセージを表示
        var msg = new gadgets.MiniMessage(prefs.getModuleId(), $('#mini_message')[0]);
        Sateraito.MiniMessage.message = msg.createStaticMessage(aMessageText);
        Sateraito.MiniMessage.message.style.fontSize = '' + Sateraito.MiniMessage.fontSize + 'px';
      }
		}
	};
	
	Sateraito.EventController = {
		MAX_RETRY: 10
	};

	Sateraito.GadgetSetting = {
		
		settingName : null,
		settingObj: {},
		mySiteUrl: null,
		
		/**
		 * init
		 *
		 * @param {string} aSettingName ... 設定ガジェット名
		 * @param {string} aMySiteUrl
		 */
		init: function(aSettingName, aMySiteUrl)
		{
			Sateraito.GadgetSetting.settingName = aSettingName;
			Sateraito.GadgetSetting.mySiteUrl = aMySiteUrl;
		},
		
		/**
		 * requestGetGadgetSetting
		 *
		 * サーバーサイドガジェットクッキーを読み込む
		 *
		 * @param {Function} callback
		 * @param {Number} aNumRetry
		 */
		requestGetGadgetSetting: function(callback, aNumRetry)
		{
			if (typeof(aNumRetry) == 'undefined') {
				aNumRetry = 1;
			}

      var baseUrl = Sateraito.GadgetSetting.mySiteUrl;
      var methodUrl = '/getgadgetsetting?setting_name=' + Sateraito.GadgetSetting.settingName;

      SimpleRequest.get({
        baseUrl: baseUrl,
        methodUrl: methodUrl,
        enableRetry: true,
        callback: function(jsondata){
          if (jsondata.is_error) {
            // エラー
            Sateraito.Util.console(jsondata.error_code);
            callback(null);
          } else {
            Sateraito.GadgetSetting.settingObj = gadgets.json.parse(decodeURI(jsondata.setting_value));
            callback(Sateraito.GadgetSetting.settingObj);
          }
        }
      });
			
			/*gadgets.io.makeRequest(Sateraito.GadgetSetting.mySiteUrl + '/getgadgetsetting?setting_name=' + Sateraito.GadgetSetting.settingName, function(response){

				if (!response.data) {

					// response error
					var err = response.errors[0];
					Sateraito.Util.console(err);

					var prefs = new gadgets.Prefs();
					Sateraito.MiniMessage.showTimerMessage(prefs.getMsg('RELOADING') + aNumRetry);
					
					if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
						Sateraito.GadgetSetting.requestGetGadgetSetting(callback, aNumRetry + 1);
					} else {
						// １０回リトライしたがだめだった
						Sateraito.MiniMessage.showTimerMessage(prefs.getMsg('ERROR_WHILE_LOADING'), 10);
					}

					return;
				}

				var jsondata = response.data;

				if (jsondata.is_error) {
					// エラー
					Sateraito.Util.console(jsondata.error_code);
					callback(null);
				} else {
					Sateraito.GadgetSetting.settingObj = gadgets.json.parse(decodeURI(jsondata.setting_value));
					callback(Sateraito.GadgetSetting.settingObj);
				}

			}, Sateraito.Util.requestParam());*/
		},
		
		/**
		 * requestSetGadgetSetting
		 *
		 * サーバーサイドガジェットクッキーを保存する
		 *
		 * @param {Object} aSettingObj
		 * @param {Function} callback
		 * @param {Number} aNumRetry
		 */
		requestSetGadgetSetting: function(aSettingObj, callback, aNumRetry)
		{
			if (typeof(aNumRetry) == 'undefined') {
				aNumRetry = 1;
			}
			
			var settingValue = encodeURI(gadgets.json.stringify(aSettingObj));
			
			var postData = {
				'setting_name': Sateraito.GadgetSetting.settingName,
				'setting_value': settingValue
			};

      var baseUrl = Sateraito.GadgetSetting.mySiteUrl;
      var methodUrl = '/setgadgetsetting';

      SimpleRequest.post({
        baseUrl: baseUrl,
        methodUrl: methodUrl,
        postData: postData,
        enableRetry: true,
        callback: function(jsondata){
          callback();
        }
      });
			
			/*gadgets.io.makeRequest(Sateraito.GadgetSetting.mySiteUrl + '/setgadgetsetting', function(response){

				if (!response.data) {

					// response error
					var err = response.errors[0];

					var prefs = new gadgets.Prefs();
					Sateraito.MiniMessage.showTimerMessage(prefs.getMsg('RELOADING') + aNumRetry);
					
					if (aNumRetry < Sateraito.EventController.MAX_RETRY) {
						Sateraito.GadgetSetting.requestSetGadgetSetting(aSettingObj, callback, (aNumRetry + 1));
					} else {
						// １０回リトライしたがだめだった
						Sateraito.MiniMessage.showTimerMessage(prefs.getMsg('ERROR_WHILE_LOADING'), 10);
					}

					return;
				}

				var jsondata = response.data;
				callback();
				
			}, Sateraito.Util.requestParam(true, postData));*/
		}
	};
	
})();
