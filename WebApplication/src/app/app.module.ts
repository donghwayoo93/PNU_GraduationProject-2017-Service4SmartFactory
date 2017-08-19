import { HttpModule } from '@angular/http';
import { BrowserModule } from '@angular/platform-browser';
import { ErrorHandler, NgModule } from '@angular/core';
import { IonicApp, IonicErrorHandler, IonicModule } from 'ionic-angular';
import { IonicStorageModule } from '@ionic/storage';

import { MyApp } from './app.component';
import { LoginPage } from '../pages/login/login'
import { SignupPage } from '../pages/signup/signup'
import { MenuPage } from '../pages/menu/menu'
import { ControlMachinePage } from '../pages/control-machine/control-machine';

import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { AuthProvider } from '../providers/auth/auth';
import { MachinesProvider } from '../providers/machines/machines';


@NgModule({
  declarations: [
    MyApp,
    LoginPage,
    SignupPage,
    MenuPage,
    ControlMachinePage
  ],
  imports: [
    BrowserModule,
    HttpModule,
    IonicModule.forRoot(MyApp),
    IonicStorageModule.forRoot({
      name: '__mydb',
      driverOrder: ['indexeddb', 'sqllite', 'websql']
    })
  ],
  bootstrap: [IonicApp],
  entryComponents: [
    MyApp,
    LoginPage,
    SignupPage,
    MenuPage,
    ControlMachinePage
  ],
  providers: [
    StatusBar,
    SplashScreen,
    { provide: ErrorHandler, useClass: IonicErrorHandler },
    AuthProvider,
    MachinesProvider
  ]
})
export class AppModule { }
