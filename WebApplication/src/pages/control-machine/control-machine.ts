import { Component } from '@angular/core';
import { Http } from '@angular/http';
import { NavController, NavParams, LoadingController } from 'ionic-angular';
import { MachinesProvider } from '../../providers/machines/machines';

@Component({
	selector: 'page-control-machine',
	templateUrl: 'control-machine.html',
})
export class ControlMachinePage {

	machineID: any;
	manualNum: any;
	loading: any;

	machineDatas = [
		{
			"title": "조회 필요",
			"content": "조회 필요"
		}
	];

	sensorDatas = [
		{
			"title": "조회 필요",
			"content": "조회 필요"
		}
	];

	manuals = [
		'조회 필요'
	];

	data = {
		one: false,
		two: false,
		three: false
	};

	constructor(public navCtrl: NavController, public navParams: NavParams,
		public machineService: MachinesProvider, private http: Http,
		public loadingCtrl: LoadingController) {
	}

	refreshPage1(page) {
		this.showLoader("설비 정보 가져오는 중...");
		let credentials = {};

		// 기기 정보
		this.machineService.getMachineInformation(credentials).then((result) => {
			this.loading.dismiss();
			var machineID = result[0].machineID;
			var accessLevel = result[0].accessLevel;
			var machineName = result[0].name;
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
		}, (err) => {
			this.loading.dismiss();
			console.log(err);
		});


	}

	refreshPage2(page) {
		this.showLoader("설비 정보 가져오는 중...");
		let credentials = {};

		// 센서 데이터
		this.machineService.getMachineSensorData(credentials).then((result) => {
			this.loading.dismiss();
			var SensorState = result[0].sensorState[0];
			this.sensorDatas = [];
			for (var idx in SensorState) {
				this.sensorDatas.push({
					"title": "센서명 : " + idx,
					"content": SensorState[idx]
				});
			}
		}, (err) => {
			this.loading.dismiss();
			console.log(err);
		});
	}

	refreshPage3(page) {
		this.showLoader("설비 정보 가져오는 중...");
		let credentials = {};
		// 지시사항
		this.machineService.getMachineManual(credentials).then((result) => {
			this.loading.dismiss();
			var manual = result[0].manual[0].instruction;
			console.log(manual);
			this.manuals = [];
			for (var idx2 in manual) {
				this.manuals.push(
					manual[idx2]
				);
			}
		}, (err) => {
			this.loading.dismiss();
			console.log(err);
		});
	}

	showLoader(content) {
		this.loading = this.loadingCtrl.create({
			content: content
		});

		this.loading.present();
	}
}
