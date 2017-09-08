import { Component } from '@angular/core';
import { NavController, NavParams, LoadingController, ToastController } from 'ionic-angular';
import { MachinesProvider } from '../../providers/machines/machines';

@Component({
	selector: 'page-control-machine',
	templateUrl: 'control-machine.html',
})
export class ControlMachinePage {

	machineID: any;
	manualNum: any;
	loading: any;

	machineDatas: any = [
		{
			"title": "Need refresh",
			"content": "Need refresh"
		}
	];

	sensorDatas: any = [
		{
			"title": "Need refresh",
			"content": "Need refresh"
		}
	];

	manuals: any = [
		{
			"instruction": "Need refresh",
			"photoNum": ""
		}
	];


	constructor(public navCtrl: NavController, public navParams: NavParams,
		public machineService: MachinesProvider, public loadingCtrl: LoadingController,
		private toastCtrl: ToastController) {

	}

	refreshPageTest(page) {
		this.manuals = [];
		this.manuals.push({
			"instruction": "물 끓이기",
			"photoNum": "../../assets/images/3.png"
		});
		this.manuals.push({
			"instruction": "면 넣기",
			"photoNum": "../../assets/images/1.png"
		});
		this.manuals.push({
			"instruction": "스프넣기",
			"photoNum": "../../assets/images/4.png"
		});

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
					"title": "Name",
					"content": machineName
				}, {
					"title": "Access Level",
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
			//[{"manual":[{"instruction":["냄비 열기","물 끓이기","라면 넣기","스프넣기","3분간 끓이기"],"num":"1"}]}]
			console.log(result);
			var manual = result[0].manual[0].instruction;
			var manualNum = result[0].manual[0].num;
			console.log(manual);

			var photoNum = [];
			if (manualNum == 1) {
				photoNum = [4, 3, 2, 1, 3];
			} else if (manualNum == 2) {
				photoNum = [1, 2, 3, 4];
			} else {
				photoNum = [3, 3, 3, 4];
			}
			this.manuals = [];
			for (var idx2 in manual) {
				this.manuals.push({
					"instruction": manual[idx2],
					"photoNum": "../../assets/images/" + photoNum[idx2] + ".png"
				});
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

	presentToast(message) {
		let toast = this.toastCtrl.create({
			message: message,
			duration: 3000,
			position: 'top'
		});
		toast.present();
	}
}
