import { Injectable } from '@angular/core';
import { Http, Headers } from '@angular/http';
import { AuthProvider } from '../auth/auth'
import 'rxjs/add/operator/map';

@Injectable()
export class MachinesProvider {

  constructor(public http: Http, public authService: AuthProvider) {
    //console.log('Hello MachinesProvider Provider');
  }

  getMachineData(option) {
    return new Promise((resolve, reject) => {
      let headers = new Headers();
      headers.append('Authorization', this.authService.token);
      this.http.get('http://localhost:8080/api/machines/machinesData/' + option.machineID, { headers: headers })
        .map(res => res.json())
        .subscribe(data => {
          resolve(data);
        }, (err) => {
          reject(err);
        });
    });
  }

  getMachineManual() {

  }
}
