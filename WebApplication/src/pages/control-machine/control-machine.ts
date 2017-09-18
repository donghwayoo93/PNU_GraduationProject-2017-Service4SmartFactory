import { Component } from '@angular/core';
import { NavController, NavParams, LoadingController, ToastController, ActionSheetController, AlertController } from 'ionic-angular';

import { LoginPage } from '../login/login';

import { MachinesProvider } from '../../providers/machines/machines';
import { ConnectionProvider } from '../../providers/connection/connection';

@Component({
	selector: 'page-control-machine',
	templateUrl: 'control-machine.html',
})
export class ControlMachinePage {

	machineID: any;
	manualNum: any;
	loading: any;
	machineDatas: Array<{ title: string, content: string }>;
	sensorDatas: Array<{ title: string, content: string }>;
	manuals: Array<{ instruction: string, photoNum: string }>;


	constructor(public navCtrl: NavController, public navParams: NavParams,
		public machineService: MachinesProvider, public loadingCtrl: LoadingController,
		private toastCtrl: ToastController, public ConnectionService: ConnectionProvider,
		private actionSheetCtrl: ActionSheetController, private alertCtrl: AlertController) {

	}

	ionViewDidLoad() {
		setInterval(() => {
			this.getRSSI();
		}, 30000)
	}

	refreshMachineInfo() {
		this.showLoader("Bringing machine information...");
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

	refreshSensorStatus() {
		this.showLoader("Bringing sensor status...");
		let credentials = {};

		// 센서 데이터
		this.machineService.getMachineSensorData(credentials).then((result) => {
			this.loading.dismiss();
			var SensorState = result[0].sensorState[0];
			this.sensorDatas = [];
			for (var idx in SensorState) {
				this.sensorDatas.push({
					"title": "Sensor Name : " + idx,
					"content": SensorState[idx]
				});
			}
		}, (err) => {
			this.loading.dismiss();
			console.log(err);
		});
	}

	refreshMachineManual() {
		this.showLoader("Bringing manuals...");
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

	controlMotor(type) {
		this.showLoader("loading...");
		this.loading.dismiss();
		if (type == "on") {
			this.machineService.turnOnMotor().then((result) => {
				console.log(result);
				if (result[0] == 'TRUE') {
					this.presentToast("success turning on");
				} else {
					this.presentToast("Failed to turn on");
				}
			}, (err) => {
				this.presentToast("Failed to turn on");
			})
		} else if (type == "off") {
			this.machineService.turnOffMotor().then((result) => {
				console.log(result);
				if (result[0] == 'TRUE') {
					this.presentToast("success turning off");
				} else {
					this.presentToast("Failed to turn off");
				}
			}, (err) => {
				this.presentToast("Failed to turn off");
			})
		}
	}

	disconnect() {
		this.showLoader("disconnect...");
		this.ConnectionService.tryDisconnect().then((result) => {
			console.log(result[0]);
			if (result[0] == "TRUE") {
				this.presentToast("Success disconnecting");
				this.loading.dismiss();
				this.navCtrl.setRoot(LoginPage);
			}
		}, (err) => {
			this.presentToast("Failed to disconnect");
			this.loading.dismiss();
		});
	}

	getRSSI() {
		this.ConnectionService.getRSSI().then((result) => {
			console.log(result);
			console.log(result[0]);
			if (0 < result[0] && result[0] < 50) {
				console.log("0~50");
				this.showDistanceAlert();
			} else if (result[0] < 0) {
				console.log("0 이하");
			} else {
				console.log("50 이상");
			}
		}, (err) => {
			console.log('failed to get RSSI');
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

	openMenu() {
		let actionSheet = this.actionSheetCtrl.create({
			//title: 'Refresh data',
			buttons: [
				{
					text: 'Machine Information',
					icon: 'refresh',
					handler: () => {
						console.log('Machine info clicked');
						this.refreshMachineInfo();
					}
				}, {
					text: 'Sensor Status',
					icon: 'refresh',
					handler: () => {
						console.log('Sensor clicked');
						this.refreshSensorStatus();
					}
				}, {
					text: 'Instructions',
					icon: 'refresh',
					handler: () => {
						console.log('Instructions clicked');
						this.refreshMachineManual();
					}
				}, {
					text: 'Disconnect',
					role: 'destructive',
					icon: 'exit',
					handler: () => {
						this.showDisconnectConfirm();
						console.log('disconnect clicked');
					},
					cssClass: "danger"
				}, {
					text: 'Cancel',
					role: 'cancel',
					handler: () => {
						console.log('Cancel clicked');
					}
				}
			]
		});
		actionSheet.present();
	}

	showDisconnectConfirm() {
		let confirm = this.alertCtrl.create({
			title: 'Do you really want to disconnect from machine?',
			message: 'You must reconnect with this or other mahcines. \nThen you can use this application again.',
			buttons: [
				{
					text: 'Disagree',
					handler: () => {
						console.log('Disagree clicked');
					}
				},
				{
					text: 'Agree',
					handler: () => {
						console.log('Agree clicked');
						this.disconnect();
					}
				}
			]
		});
		confirm.present();
	}
	showDistanceAlert() {
		let alert = this.alertCtrl.create({
			title: "distance alert",
			message: "You're far from mahcine.\nhold nearby position",
			buttons: ['OK']
		});
		alert.present();
	}
}
