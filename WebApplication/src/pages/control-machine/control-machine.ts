import { Component } from '@angular/core';
import { NavController, NavParams, LoadingController, ToastController, ActionSheetController, AlertController } from 'ionic-angular';
import { Storage } from '@ionic/storage';

import { LoginPage } from '../login/login';

import { MachinesProvider } from '../../providers/machines/machines';
import { ConnectionProvider } from '../../providers/connection/connection';

import * as highchart from 'highcharts';
import * as highchartsMore from 'highcharts-more';
highchartsMore(highchart);


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
	intervalRSSI: any;
	intervalGauge: any;
	chartPhoto: any;
	chartMotor: any;
	chartSolar: any;
	chartBasic: any;
	alert: any;

	constructor(public navCtrl: NavController, public navParams: NavParams,
		public machineService: MachinesProvider, public loadingCtrl: LoadingController,
		private toastCtrl: ToastController, public ConnectionService: ConnectionProvider,
		private actionSheetCtrl: ActionSheetController, private alertCtrl: AlertController,
		public storage: Storage, ) {
	}

	ionViewDidLoad() {
		this.refreshMachineInfo();
		this.makeSolarGauge();
		this.makePhotoGauge();
		this.makeMotorGauge();
		this.makeBasicChart();
		this.intervalRSSI = setInterval(() => {
			this.getRSSI();
		}, 30000);
		this.intervalGauge = setInterval(() => {
			this.refreshGauge();
		}, 5000);
	}

	refreshMachineInfo() {
		this.showLoader("Bringing machine information...");
		//let credentials = {};

		this.storage.get('accessLevel').then(userAccessLevel => {
			this.storage.get('machineID').then(machineID => {
				this.storage.get('machineName').then(machineName => {
					console.log(userAccessLevel + " / " + machineID + " / " + machineName);
					this.machineDatas = [
						{
							"title": "ID",
							"content": machineID
						}, {
							"title": "Name",
							"content": machineName
						}, {
							"title": "Access Level",
							"content": userAccessLevel
						}
					];
					this.loading.dismiss();
				}, (err) => {
					this.loading.dismiss();
					console.log(err);
				});
			}, (err) => {
				this.loading.dismiss();
				console.log(err);
			});
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
			console.log(result);
			var manual = result[0].manual[0].instruction;
			var manualNum = result[0].manual[0].num;
			console.log(manual);

			var photoNum: Array<String>;
			if (manualNum == 0) {
				photoNum = ["0.gif"];
			} else if (manualNum == 1) {
				photoNum = ["non.png", "non.png", "switch_1.png", "non.png", "non.png"];
			} else if (manualNum == 2) {
				photoNum = ["non.png", "non.png", "switch_2.png", "non.png", "non.png"];
			} else if (manualNum == 3) {
				photoNum = ["3.png", "3.png", "3.png", "3.png", "3.png"];
			} else if (manualNum == 4) {
				photoNum = ["4.png", "4.png", "4.png", "4.png", "4.png"];
			} else {
				photoNum = ["0.gif"];
			}
			this.manuals = [];
			for (var idx2 in manual) {
				this.manuals.push({
					"instruction": manual[idx2],
					"photoNum": "./assets/images/" + photoNum[idx2]
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
				clearInterval(this.intervalRSSI);
				clearInterval(this.intervalGauge);
			}
		}, (err) => {
			this.presentToast("Failed to disconnect");
			this.loading.dismiss();
		});
	}

	getRSSI() {
		this.ConnectionService.getRSSI().then((result) => {
			console.log("rss: " + result[0]);
			if (0 < result[0] && result[0] < 60) {
				//console.log("0~50");
			} else if (result[0] < 0) {
				//console.log("0 이하");
			} else {
				//console.log("50 이상");
				this.showDistanceAlert();
			}
		}, (err) => {
			console.log('failed to get RSSI');
		});
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

	showDistanceAlert() {
		this.alert = this.alertCtrl.create({
			title: "distance alert",
			message: "You're far from mahcine.\nhold nearby position",
			buttons: ['OK']
		});
		this.alert.present();
	}

	refreshGauge() {
		this.machineService.refreshGauge().then((result) => {
			var a = JSON.parse(result[0]);
			console.log(a);
			this.chartSolar.series[0].points[0].update(parseInt(a.solar));
			this.chartPhoto.series[0].points[0].update(parseInt(a.photosynthetic));
			this.chartMotor.series[0].points[0].update((parseInt(a.motor) == 0) ? 1 : 3);
		}, (err) => {
			console.log(err);
		});
	}

	makeSolarGauge() {
		this.chartSolar = highchart.chart('chartSolar', {
			chart: {
				type: 'gauge',
				plotBackgroundColor: null,
				plotBackgroundImage: null,
				plotBorderWidth: 0,
				plotShadow: false
			},
			title: {
				text: 'solar'
			},
			pane: {
				startAngle: -160,
				endAngle: 160,
				background: []
			},
			// the value axis
			yAxis: {
				min: 0,
				max: 5000,

				minorTickInterval: 'auto',
				minorTickWidth: 1,
				minorTickLength: 10,
				minorTickPosition: 'inside',
				minorTickColor: '#666',

				tickPixelInterval: 30,
				tickWidth: 2,
				tickPosition: 'inside',
				tickLength: 10,
				tickColor: '#666',
				labels: {
					step: 4,
					rotation: 'auto'
				},
				title: {
					text: 'lux'
				},
				plotBands: [{
					from: 0,
					to: 1000,
					color: '#DF5353' // red
				}, {
					from: 1000,
					to: 1500,
					color: '#DDDF0D' // yellow
				}, {
					from: 1500,
					to: 3500,
					color: '#55BF3B' // green
				}, {
					from: 3500,
					to: 4000,
					color: '#DDDF0D' // yellow
				}, {
					from: 4000,
					to: 5000,
					color: '#DF5353' // red
				}]
			},

			series: [{
				name: 'Solar',
				data: [0],
				tooltip: { valueSuffix: " lux" }
			}]
		})
	}

	makePhotoGauge() {
		this.chartPhoto = highchart.chart('chartPhoto', {
			chart: {
				type: 'gauge'
			},

			title: {
				text: 'Photosynthetic'
			},

			pane: {
				startAngle: -160,
				endAngle: 160,
				background: []
			},

			// the value axis
			yAxis: {
				min: 0,
				max: 500,

				minorTickInterval: 'auto',
				minorTickWidth: 1,
				minorTickLength: 10,
				minorTickPosition: 'inside',
				minorTickColor: '#666',

				tickPixelInterval: 30,
				tickWidth: 2,
				tickPosition: 'inside',
				tickLength: 10,
				tickColor: '#666',
				labels: {
					step: 4,
					rotation: 'auto'
				},
				title: {
					text: 'lux'
				},
				plotBands: [{
					from: 0,
					to: 100,
					color: '#DF5353' // red
				}, {
					from: 100,
					to: 150,
					color: '#DDDF0D' // yellow
				}, {
					from: 150,
					to: 350,
					color: '#55BF3B' // green
				}, {
					from: 350,
					to: 400,
					color: '#DDDF0D' // yellow
				}, {
					from: 400,
					to: 500,
					color: '#DF5353' // red
				}]
			},

			series: [{
				name: 'Photosynthetic',
				data: [0],
				tooltip: {
					valueSuffix: ' lux'
				}
			}]
		});
	}

	makeMotorGauge() {
		this.chartMotor = highchart.chart('chartMotor', {
			chart: {
				type: 'gauge'
			},
			title: {
				text: 'Motor'
			},
			pane: {
				startAngle: -90,
				endAngle: 90,
				background: []
			},
			// the value axis
			yAxis: {
				min: 0,
				max: 4,

				tickPixelInterval: 50,
				tickWidth: 4,
				tickPosition: 'inside',
				tickLength: 0,
				tickColor: '#666',
				labels: {
					step: 40,
					rotation: 'auto'
				},
				title: {
					text: 'OFF | ON'
				},
				plotBands: [{
					from: 2,
					to: 4,
					color: '#55BF3B' // green
				}, {
					from: 0,
					to: 2,
					color: '#DF5353' // red
				}]
			},

			series: [{
				name: 'Motor',
				data: [0]
			}]
		});
	}

	makeBasicChart() {
		this.machineService.getMachineSensorData().then((result) => {
			console.log(result);

			var solarValueArray = [], photoValueArray = [];

			for (var i = 0; i < 11; i++) {
				if (result[i].length != 0) {
					solarValueArray.push(result[i][0].A);
				} else {
					solarValueArray.push(null);
				}
				if (result[(i + 11)].length != 0) {
					photoValueArray.push(result[(i + 11)][0].A);
				} else {
					photoValueArray.push(null);
				}
			}

			console.log(solarValueArray);
			console.log(photoValueArray);

			this.chartBasic = highchart.chart('chartBasic', {
				title: {
					text: 'sensor history'
				},
				xAxis: {
					type: 'datetime'
				},
				legend: {
					layout: 'horizontal',
					align: 'center',
					verticalAlign: 'bottom'
				},

				plotOptions: {
					series: {
						// 1시간 단위로 하루치
						pointStart: Date.UTC(new Date().getFullYear(), new Date().getMonth(), new Date().getDate(), new Date().getHours() - 12),
						pointInterval: 3600 * 1000
					}
				},

				series: [{
					name: 'solar',
					data: solarValueArray
				}, {
					name: 'photosynthetic',
					data: photoValueArray
				}],

				responsive: {
					rules: [{
						condition: {
							maxWidth: 500
						},
						chartOptions: {
							legend: {
								layout: 'horizontal',
								align: 'center',
								verticalAlign: 'bottom'
							}
						}
					}]
				}
			});
		}, (err) => {
			console.log(err);
		});

	}
}
