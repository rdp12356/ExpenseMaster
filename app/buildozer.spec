
[app]
title = ExpenseMaster
package.name = expensemaster
package.domain = org.expense.master
source.dir = .
source.include_exts = py,kv,json,env
version = 0.1.0
requirements = python3,kivy,requests,pydantic,python-dotenv,httpx,babel,matplotlib,supabase
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 24
android.archs = arm64-v8a,armeabi-v7a
android.manifest.intent_filters = \
    <intent-filter>\
        <action android:name="android.intent.action.VIEW" />\
        <category android:name="android.intent.category.DEFAULT" />\
        <category android:name="android.intent.category.BROWSABLE" />\
        <data android:scheme="http" android:host="127.0.0.1" android:pathPrefix="/callback" />\
    </intent-filter>

[buildozer]
log_level = 2
warn_on_root = 1
