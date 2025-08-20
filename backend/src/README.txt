■ ガジェット下の「サテライトオフィス・Myポータルガジェット for Google Apps」表示（広告）を消す方法
  ・データストア「GoogleAppsDomainEntry」の「hide_ad」をTrueに設定すると、そのドメインは広告が非表示になります。

■ サテライトオフィス・Myポータルガジェットで、マルチドメイン設定をする場合の手順について
  １．プライマリードメインのGoogleAppsDomainEntryに、multi_domain_setting=Trueを設定する
  ２．ユーザーには、プライマリードメインのガジェット（ガジェットURLの一部がプライマリードメインになっているガジェット）を使って下さい！と連絡する
  ３．以上で設定はOK

***** 上記の２つの方法ではGAE管理コンソールからGoogleAppsDomainEntryを直接編集しますが、GoogleAppsDomainEntryは最長１２時間memcacheにキャッシュされるので、
      すぐには変更は反映されません。
      上記２つの変更をおこなったあとはGAE管理コンソールからmemcacheをクリアして下さい。 *****

■ メールアドレスが変更になったユーザーについて
  ・メールアドレスが変更になったユーザーは、ガジェットに再度「認証する」リンクが表示されるようになります。
  ・認証するリンクをクリックすることで再認証され、正しい内容が表示されるようになります。

■ ガジェットの認証先ドメインの変更について（2014-01-16）
  ・通常ガジェットの認証先ドメインはガジェットURLに埋め込まれているドメインへ認証しに行きます。
    （ガジェットの初回表示で「認証する」リンクをクリックしたときにログインに行くドメイン）
  ・このドメインを変えたい場合、
    （ケースとしてはプライマリがほとんど人のいないドメインで、サブドメインがほとんどのユーザーの所属するドメインの場合
     ほとんどのユーザーがマルチドメイン設定による「その他のドメインはこちら」リンククリック＆ドメイン名入力になってしまう場合）
    GoogleAppsDomainEntry.gadget_auth_linkにサブドメインを設定することにより
      --> リンク表示が一つになります（「認証する」だけになります）
          「認証する」をクリックした場合にgadget_auth_linkに設定したドメインへ認証しに行きます
  ・GoogleAppsDomainEntry.gadget_auth_linkの設定を削除すると、もとの動作に戻ります。

::KEY IMPORTANT::
TODO:: only_dev => It's code just run in dev mode. When release, you need check anh double check TODO:: only_dev and fix to run in release mode