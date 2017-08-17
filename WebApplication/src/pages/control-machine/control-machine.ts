import { Component } from '@angular/core';
import { Http } from '@angular/http';
import { NavController, NavParams } from 'ionic-angular';
import { MachinesProvider } from '../../providers/machines/machines'

@Component({
	selector: 'page-control-machine',
	templateUrl: 'control-machine.html',
})
export class ControlMachinePage {
	filePath = 'assets/tempData.json';
	machineID: any;
	manualNum: any;

	machineDatas = [
		{
			"title": "조회 필요",
			"content": "조회 필요"
		}
	];

	manuals = [
		'조회 필요'
	];

	constructor(public navCtrl: NavController, public navParams: NavParams,
		public machineService: MachinesProvider, private http: Http) {
	}

	refreshPage(page) {
		return this.http.get(this.filePath)
			.map((res) => {
				return res.json()
			}).subscribe(actual_JSON => {
				console.log(actual_JSON);

				var machineID = actual_JSON.machineID;
				var accessLevel = actual_JSON.accessLevel;
				var isLogin = actual_JSON.isLogin;
				var SensorState = actual_JSON.sensorState;
				var machineName = actual_JSON.name;
				var manual = actual_JSON.manual;
				console.log(manual);
				this.machineDatas = [
					{
						"title": "ID",
						"content": machineID
					}, {
						"title": "name",
						"content": machineName
					}, {
						"title": "access level",
						"content": accessLevel
					}
				];

				for (var idx in SensorState) {
					this.machineDatas.push({
						"title": "센서명 : " + idx,
						"content": SensorState[idx]
					});
				}
				this.manuals = [];
				for (var idx2 in manual) {
					this.manuals.push(
						manual[idx2]
					);
				}
			});
	}

}
