"use strict";(self.webpackChunkz4d_plugin=self.webpackChunkz4d_plugin||[]).push([[506],{90506:(F,m,s)=>{s.r(m),s.d(m,{ManufacturerModule:()=>z});var Z=s(44466),d=s(27633),p=s(88648);class C{constructor(o,a){this.IRCode=o,this.NwkId=a}}var e=s(5e3),_=s(5830),g=s(22290),u=s(27232),c=s(46166);const U=["table"];function T(t,o){1&t&&e._uU(0),2&t&&e.hij("\n            ",o.row.NwkId,"\n          ")}function y(t,o){1&t&&e._uU(0),2&t&&e.hij("\n            ",o.row.Name,"\n          ")}function v(t,o){1&t&&e._uU(0),2&t&&e.hij("\n            ",o.row.IEEE,"\n          ")}function A(t,o){1&t&&e._uU(0),2&t&&e.hij("\n            ",o.row.Model,"\n          ")}function w(t,o){if(1&t){const a=e.EpF();e._uU(0,"\n            "),e.TgZ(1,"input",15),e.NdJ("change",function(i){const r=e.CHM(a).row,Q=e.oxw();return e.KtG(Q.updateIRCode(i,r.NwkId))}),e.qZA(),e._uU(2,"\n          ")}if(2&t){const a=o.row;e.xp6(1),e.Q6J("value",a.IRCode)}}const x=function(t,o,a){return{emptyMessage:t,totalMessage:o,selectedMessage:a}};new p.Yd("CasaiaComponent");let b=(()=>{class t{constructor(a,n,i){this.apiService=a,this.toastr=n,this.translate=i,this.temp=[],this.hasEditing=!1}ngOnInit(){this.getCasaiaDevices()}updateIRCode(a,n){this.hasEditing=!0,this.rows.find(l=>l.NwkId===n).IRCode=a.target.value}updateCasaiaDevices(){const a=[];this.rows.forEach(n=>{a.push(new C(n.IRCode,n.NwkId))}),this.apiService.putCasiaIrcode(a).subscribe(n=>{this.hasEditing=!1,this.getCasaiaDevices(),this.toastr.success(this.translate.instant("api.global.succes.update.notify"))})}updateFilter(a){const n=a.target.value.toLowerCase(),i=this.temp.filter(function(l){let r=!1;return l.Model&&(r=-1!==l.Model.toLowerCase().indexOf(n)),!r&&l.NwkId&&(r=-1!==l.NwkId.toLowerCase().indexOf(n)),!r&&l.IEEE&&(r=-1!==l.IEEE.toLowerCase().indexOf(n)),!r&&l.Name&&(r=-1!==l.Name.toLowerCase().indexOf(n)),!r&&l.IRCode&&(r=-1!==l.IRCode.toLowerCase().indexOf(n)),r||!n});this.rows=i,this.table.offset=0}getCasaiaDevices(){this.apiService.getCasiaDevices().subscribe(a=>{this.rows=a,this.temp=[...this.rows]})}}return t.\u0275fac=function(a){return new(a||t)(e.Y36(_.s),e.Y36(g._W),e.Y36(u.sK))},t.\u0275cmp=e.Xpm({type:t,selectors:[["app-manufacturer-casaia"]],viewQuery:function(a,n){if(1&a&&e.Gf(U,5),2&a){let i;e.iGM(i=e.CRH())&&(n.table=i.first)}},decls:59,vars:45,consts:[[1,"card"],[1,"card-header"],[1,"btn","btn-primary","float-right",3,"disabled","translate","click"],[1,"card-body"],[1,"card-title",3,"innerHTML"],[1,"card-text"],["type","text",3,"placeholder","keyup"],[1,"bootstrap",3,"rows","columnMode","headerHeight","footerHeight","limit","rowHeight","messages"],["table",""],["prop","NwkId",3,"name"],["ngx-datatable-cell-template",""],["prop","Name",3,"name"],["prop","IEEE",3,"name"],["prop","Model",3,"name"],["prop","IRCode",3,"name"],["autofocus","","type","text","size","4","maxlength","4",3,"value","change"]],template:function(a,n){1&a&&(e.TgZ(0,"div",0),e._uU(1,"\n  "),e.TgZ(2,"div",1),e._uU(3),e.ALo(4,"translate"),e.TgZ(5,"button",2),e.NdJ("click",function(){return n.updateCasaiaDevices()}),e.ALo(6,"translate"),e.qZA(),e._uU(7,"\n  "),e.qZA(),e._uU(8,"\n  "),e.TgZ(9,"div",3),e._uU(10,"\n    "),e._UZ(11,"h5",4),e.ALo(12,"translate"),e._uU(13,"\n    "),e.TgZ(14,"div",5),e._uU(15,"\n      "),e.TgZ(16,"input",6),e.NdJ("keyup",function(l){return n.updateFilter(l)}),e.ALo(17,"translate"),e.qZA(),e._uU(18,"\n      "),e.TgZ(19,"ngx-datatable",7,8),e.ALo(21,"translate"),e.ALo(22,"translate"),e.ALo(23,"translate"),e._uU(24,"\n        "),e.TgZ(25,"ngx-datatable-column",9),e.ALo(26,"translate"),e._uU(27,"\n          "),e.YNc(28,T,1,1,"ng-template",10),e._uU(29,"\n        "),e.qZA(),e._uU(30,"\n        "),e.TgZ(31,"ngx-datatable-column",11),e.ALo(32,"translate"),e._uU(33,"\n          "),e.YNc(34,y,1,1,"ng-template",10),e._uU(35,"\n        "),e.qZA(),e._uU(36,"\n        "),e.TgZ(37,"ngx-datatable-column",12),e.ALo(38,"translate"),e._uU(39,"\n          "),e.YNc(40,v,1,1,"ng-template",10),e._uU(41,"\n        "),e.qZA(),e._uU(42,"\n        "),e.TgZ(43,"ngx-datatable-column",13),e.ALo(44,"translate"),e._uU(45,"\n          "),e.YNc(46,A,1,1,"ng-template",10),e._uU(47,"\n        "),e.qZA(),e._uU(48,"\n        "),e.TgZ(49,"ngx-datatable-column",14),e.ALo(50,"translate"),e._uU(51,"\n          "),e.YNc(52,w,3,1,"ng-template",10),e._uU(53,"\n        "),e.qZA(),e._uU(54,"\n      "),e.qZA(),e._uU(55,"\n    "),e.qZA(),e._uU(56,"\n  "),e.qZA(),e._uU(57,"\n"),e.qZA(),e._uU(58,"\n")),2&a&&(e.xp6(3),e.hij("\n    ",e.lcZ(4,17,"manufacturer.casaia.header"),"\n    "),e.xp6(2),e.s9C("translate",e.lcZ(6,19,"manufacturer.casaia.validate.button")),e.Q6J("disabled",!n.hasEditing),e.xp6(6),e.Q6J("innerHTML",e.lcZ(12,21,"manufacturer.casaia.subtitle"),e.oJD),e.xp6(5),e.s9C("placeholder",e.lcZ(17,23,"manufacturer.casaia.placeholder")),e.xp6(3),e.Q6J("rows",n.rows)("columnMode","force")("headerHeight",40)("footerHeight","auto")("limit",10)("rowHeight","auto")("messages",e.kEZ(41,x,e.lcZ(21,25,"NODATA"),e.lcZ(22,27,"TOTAL"),e.lcZ(23,29,"SELECTED"))),e.xp6(6),e.s9C("name",e.lcZ(26,31,"manufacturer.casaia.nwkid")),e.xp6(6),e.s9C("name",e.lcZ(32,33,"manufacturer.casaia.name")),e.xp6(6),e.s9C("name",e.lcZ(38,35,"manufacturer.casaia.ieee")),e.xp6(6),e.s9C("name",e.lcZ(44,37,"manufacturer.casaia.model")),e.xp6(6),e.s9C("name",e.lcZ(50,39,"manufacturer.casaia.ircode")))},dependencies:[u.Pi,c.nE,c.UC,c.vq,u.X$]}),t})();class k{}var L=s(54004),f=s(69808),h=s(94076),M=s(80399);const N=["table"];function E(t,o){if(1&t&&(e._uU(0,"\n          "),e.TgZ(1,"span",9),e._uU(2,"\n            "),e.TgZ(3,"b"),e._uU(4,"Name"),e.qZA(),e._uU(5),e.TgZ(6,"b"),e._uU(7,"NwkId"),e.qZA(),e._uU(8),e.qZA(),e._uU(9,"\n        ")),2&t){const a=o.item,n=o.searchTerm;e.xp6(1),e.Q6J("ngOptionHighlight",n),e.xp6(4),e.hij(" : ",a.ZDeviceName," - "),e.xp6(3),e.hij(" : ",a.Nwkid,"")}}function I(t,o){if(1&t&&(e.TgZ(0,"p",10),e._uU(1),e.ALo(2,"translate"),e.qZA()),2&t){const a=e.oxw();e.xp6(1),e.Oqu(e.lcZ(2,1,a.deviceSelected.protocole))}}function O(t,o){1&t&&(e._uU(0,"\n            "),e.TgZ(1,"span"),e._uU(2),e.ALo(3,"translate"),e.qZA(),e._uU(4,"\n          ")),2&t&&(e.xp6(2),e.Oqu(e.lcZ(3,1,"manufacturer.zlinky.key")))}function H(t,o){1&t&&(e._uU(0),e.ALo(1,"translate")),2&t&&e.hij("\n            ",e.lcZ(1,1,"manufacturer.zlinky.".concat(o.row.key)),"\n          ")}function Y(t,o){1&t&&(e._uU(0,"\n            "),e.TgZ(1,"span"),e._uU(2),e.ALo(3,"translate"),e.qZA(),e._uU(4,"\n          ")),2&t&&(e.xp6(2),e.Oqu(e.lcZ(3,1,"manufacturer.zlinky.value")))}function D(t,o){1&t&&e._uU(0),2&t&&e.hij("\n            ",o.row.value,"\n          ")}const q=function(t,o,a){return{emptyMessage:t,totalMessage:o,selectedMessage:a}};function J(t,o){if(1&t&&(e.TgZ(0,"ngx-datatable",11,12),e.ALo(2,"translate"),e.ALo(3,"translate"),e.ALo(4,"translate"),e._uU(5,"\n        "),e.TgZ(6,"ngx-datatable-column",13),e._uU(7,"\n          "),e.YNc(8,O,5,3,"ng-template",14),e._uU(9,"\n          "),e.YNc(10,H,2,3,"ng-template",15),e._uU(11,"\n        "),e.qZA(),e._uU(12,"\n        "),e.TgZ(13,"ngx-datatable-column",16),e._uU(14,"\n          "),e.YNc(15,Y,5,3,"ng-template",14),e._uU(16,"\n          "),e.YNc(17,D,1,1,"ng-template",15),e._uU(18,"\n        "),e.qZA(),e._uU(19,"\n      "),e.qZA()),2&t){const a=e.oxw();e.Q6J("rows",a.deviceSelected.ParametersForDisplay)("columnMode","force")("headerHeight",40)("footerHeight","auto")("limit",10)("rowHeight","auto")("messages",e.kEZ(13,q,e.lcZ(2,7,"NODATA"),e.lcZ(3,9,"TOTAL"),e.lcZ(4,11,"SELECTED")))}}new p.Yd("ZlinkyComponent");let S=(()=>{class t{constructor(a,n,i){this.apiService=a,this.toastr=n,this.translate=i}ngOnInit(){this.zlinkys$=this.apiService.getZlinky().pipe((0,L.U)(a=>(a.forEach(n=>{n.protocole="PROTOCOL_LINKY_"+n["PROTOCOL Linky"],n.ParametersForDisplay=[],n.Parameters.forEach(i=>{const l=new k;l.key=Object.keys(i)[0],l.value=Object.values(i)[0],n.ParametersForDisplay.push(l)})}),a)))}getConfiguration(a){this.deviceSelected=a}}return t.\u0275fac=function(a){return new(a||t)(e.Y36(_.s),e.Y36(g._W),e.Y36(u.sK))},t.\u0275cmp=e.Xpm({type:t,selectors:[["app-manufacturer-zlinky"]],viewQuery:function(a,n){if(1&a&&e.Gf(N,5),2&a){let i;e.iGM(i=e.CRH())&&(n.table=i.first)}},decls:27,vars:17,consts:[[1,"card"],[1,"card-header"],[1,"card-body"],[1,"card-title",3,"innerHTML"],[1,"card-text"],["bindLabel","ZDeviceName","appendTo","body",1,"w-25",3,"items","multiple","closeOnSelect","searchable","placeholder","change","clear"],["ng-option-tmp",""],["class","mt-3 mb-3 font-weight-bold",4,"ngIf"],["class","bootstrap",3,"rows","columnMode","headerHeight","footerHeight","limit","rowHeight","messages",4,"ngIf"],[3,"ngOptionHighlight"],[1,"mt-3","mb-3","font-weight-bold"],[1,"bootstrap",3,"rows","columnMode","headerHeight","footerHeight","limit","rowHeight","messages"],["table",""],["prop","key"],["ngx-datatable-header-template",""],["ngx-datatable-cell-template",""],["prop","value"]],template:function(a,n){1&a&&(e.TgZ(0,"div",0),e._uU(1,"\n  "),e.TgZ(2,"div",1),e._uU(3),e.ALo(4,"translate"),e.qZA(),e._uU(5,"\n  "),e.TgZ(6,"div",2),e._uU(7,"\n    "),e._UZ(8,"h5",3),e.ALo(9,"translate"),e._uU(10,"\n    "),e.TgZ(11,"div",4),e._uU(12,"\n      "),e.TgZ(13,"ng-select",5),e.NdJ("change",function(l){return n.getConfiguration(l)})("clear",function(){return n.deviceSelected=null}),e.ALo(14,"async"),e.ALo(15,"translate"),e._uU(16,"\n        "),e.YNc(17,E,10,3,"ng-template",6),e._uU(18,"\n      "),e.qZA(),e._uU(19,"\n\n      "),e.YNc(20,I,3,3,"p",7),e._uU(21,"\n\n      "),e.YNc(22,J,20,17,"ngx-datatable",8),e._uU(23,"\n    "),e.qZA(),e._uU(24,"\n  "),e.qZA(),e._uU(25,"\n"),e.qZA(),e._uU(26,"\n")),2&a&&(e.xp6(3),e.hij("\n    ",e.lcZ(4,9,"manufacturer.zlinky.header"),"\n  "),e.xp6(5),e.Q6J("innerHTML",e.lcZ(9,11,"manufacturer.zlinky.subtitle"),e.oJD),e.xp6(5),e.s9C("placeholder",e.lcZ(15,15,"manufacturer.zlinky.placeholder")),e.Q6J("items",e.lcZ(14,13,n.zlinkys$))("multiple",!1)("closeOnSelect",!0)("searchable",!0),e.xp6(7),e.Q6J("ngIf",n.deviceSelected),e.xp6(2),e.Q6J("ngIf",n.deviceSelected))},dependencies:[f.O5,h.w9,h.ir,c.nE,c.UC,c.tk,c.vq,M.s,f.Ov,u.X$]}),t})();const R=[{path:"casaia",component:b,data:{title:(0,p.Kl)("manufacturer.casaia")}},{path:"zlinky",component:S,data:{title:(0,p.Kl)("manufacturer.zlinky")}}];let j=(()=>{class t{}return t.\u0275fac=function(a){return new(a||t)},t.\u0275mod=e.oAB({type:t}),t.\u0275inj=e.cJS({imports:[d.Bz.forChild(R),d.Bz]}),t})(),z=(()=>{class t{}return t.\u0275fac=function(a){return new(a||t)},t.\u0275mod=e.oAB({type:t}),t.\u0275inj=e.cJS({imports:[j,Z.m]}),t})()}}]);