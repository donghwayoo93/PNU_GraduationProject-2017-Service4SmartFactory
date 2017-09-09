import { Injectable } from '@angular/core';
import { Http } from '@angular/http';
import { Storage } from '@ionic/storage';
import 'rxjs/add/operator/map';

/*
  Generated class for the ConnectionProvider provider.

  See https://angular.io/docs/ts/latest/guide/dependency-injection.html
  for more info on providers and Angular DI.
*/
@Injectable()
export class ConnectionProvider {

  constructor(public http: Http, public storage: Storage) {
    //console.log('Hello ConnectionProvider Provider');
  }

  tryConnect() {
    return new Promise((resolve, reject) => {
      this.http.get('http://localhost:9999/api/connect')
        .map(res => res.json())
        .subscribe(data => {
          resolve(data);
        }, (err) => {
          reject(err);
        });
    });
  }

  tryDisconnect() {
    return new Promise((resolve, reject) => {
      this.http.get('http://localhost:9999/api/disconnect')
        .map(res => res.json())
        .subscribe(data => {
          resolve(data);
          this.storage.set('token', '');
          this.storage.set('email', '');
          this.storage.set('accessLevel', '');
        }, (err) => {
          reject(err);
        });
    });
  }

  getRSSI() {
    return new Promise((resolve, reject) => {
      this.http.get('http://localhost:9999/api/rssi')
        .subscribe(data => {
          resolve(data);
        }, (err) => {
          reject(err);
        });
    });
  }

}
