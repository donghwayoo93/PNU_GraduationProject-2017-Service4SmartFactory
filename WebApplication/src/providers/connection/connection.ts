import { Injectable } from '@angular/core';
import { Http } from '@angular/http';
import 'rxjs/add/operator/map';

/*
  Generated class for the ConnectionProvider provider.

  See https://angular.io/docs/ts/latest/guide/dependency-injection.html
  for more info on providers and Angular DI.
*/
@Injectable()
export class ConnectionProvider {

  constructor(public http: Http) {
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
        .subscribe(data => {
          resolve(data);
        }, (err) => {
          reject(err);
        });
    });
  }

}
