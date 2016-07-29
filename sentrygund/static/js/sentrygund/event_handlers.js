current_alerts = {

	storage : {},
	add : function(new_alert) {

		alert_id = new_alert['id'];

		console.log(alert_id);

		if (!(alert_id  in this.storage) || this.storage[alert_id] === 0) {

			this.storage[alert_id] = 0;
			this.create_collapsible(new_alert);
		}
		this.storage[alert_id]++;
		console.log(this.storage[alert_id]);
		this.add_to_collapsible(new_alert);
	},
	remove : function(a) {

		this.remove_from_collapsible(a);
		this.destroy_collapsible(a['id']);
	},
	create_collapsible : function(a) {

		console.log('swag');

		alert_id = a['id'];
		ssid = a['essid'];
		bssid = a['bssid'];
		channel = a['channel'];
		intent = a['intent'];

		$('#set').append('<div data-role="collapsible" class="'+alert_id+'"><h3>'+bssid+' '+channel+' '+intent+'</h3><p></p></div>').collapsibleset('refresh');
	
		$('.'+alert_id+' p').append('<div class="tablewrap"></div>');
		$('.'+alert_id+' .tablewrap').append('<div class="overflower"></div>');
		$('.'+alert_id+' .overflower').append('<form data-ajax="false" class="'+alert_id+'form"></form>');
		$('.'+alert_id+' form').append('<span class="tablespan"></span>');
		$('.'+alert_id+' .tablespan').append('<table data-role="table" class="sel-table ui-responsive table-shadow"></table>');
		$('.'+alert_id+' .tablespan table').append('<thead></thead>');
		$('.'+alert_id+' .tablespan table').append('<tbody id="'+alert_id+'"></tbody>');
		$('.'+alert_id+' thead').append('<th>Device</th>');
		$('.'+alert_id+' thead').append('<th>Distance</th>');
		$('.'+alert_id+' thead').append('<th>TX</th>');

		$('.'+alert_id+' form').append('<fieldset data-role="controlgroup" data-type="horizontal" ></fieldset>');

		$('.'+alert_id+' fieldset').append('<input type="radio" name="radio-choice-2" id="radio-choice-21" value="choice-1" checked="checked" />');
		$('.'+alert_id+' fieldset').append('<label for="radio-choice-21">Locate</label>');
		$('.'+alert_id+' fieldset').append('<input type="radio" name="radio-choice-2" id="radio-choice-22" value="choice-2" />');
		$('.'+alert_id+' fieldset').append('<label for="radio-choice-22">Deauth</label>');
		$('.'+alert_id+' fieldset').append('<input type="radio" name="radio-choice-2" id="radio-choice-23" value="choice-3" />');
		$('.'+alert_id+' fieldset').append('<label for="radio-choice-23">Napalm</label>');
		$('.'+alert_id+' fieldset').append('<input type="radio" name="radio-choice-2" id="radio-choice-24" value="choice-4" />');
		$('.'+alert_id+' fieldset').append('<label for="radio-choice-24">Dismiss</label>');
		$('.'+alert_id+' fieldset').append('<input style="margin-left: 1em" type="submit" value="Submit"/>');
		$('.'+alert_id+' form').trigger('create');
		$('.'+alert_id+' form table').trigger('create');
	},
	destroy_collapsible : function(alert_id) {

		$('.'+alert_id).remove();
	},
	add_to_collapsible : function(a) {

		console.log('woah');
		alert_id = a['id'];
		$('#'+alert_id).empty();

		var sortable = [];
		for (var device in a['locations']) {

			sortable.push([device, a['locations'][device]]);
		}
		sortable.sort(

			function(a, b) { 

				return b[1] - a[1];
			}
		)
		for (var i = 0, len = sortable.length; i < len; i++) {
		
			var next_row = sortable[i];
			console.log('next row: '+next_row);
			console.log(i);
			console.log(len);
			$('#'+alert_id).append('<tr class="tr'+i+'">');
			$('#'+alert_id+' .tr'+i).append('<td class="device-id">'+next_row[0]+'</td>');
			$('#'+alert_id+' .tr'+i).append('<td class="distance">'+(1.0/Math.sqrt(256 + next_row[1]))+'</td>');
			$('#'+alert_id+' .tr'+i).append('<td class="tx">'+next_row[1]+'</td>');
			
		}

		console.log(sortable);
	},
	remove_from_collapsible : function(a) {

		var id = a['id'];

		$('#'+id).remove();
	},
	intent2description : function(intent) {

		return 'description goes here';
	},
	notify : function() {
		return;
	}
}
// EVENTS

/* on_alert_add()
 *
 */
function on_alert_add(e) {

	current_alerts.add(e);
}

/* on_alert_dismiss()
 *
 */
function on_alert_dismiss(e) {

	console.log(e);
	for (var i = 0; i < e.length; i++) {
		current_alerts.remove(e[i]);
	}
}

/* on_connect()
 *
 */
function on_connect(e, socket) {

	socket.emit('connected');
}

/* on_form_submit()
 *
 */
function on_form_submit(e) {

	e.preventDefault();

	var checked = $(this).find('input[type=radio]:checked')[0];
	switch (checked.value) {

		case 'choice-1':
			console.log('Locate');
			break;
		case 'choice-2':
			console.log('Deauth');
			deauth_targets(this);
			break;
		case 'choice-3':
			console.log('Napalm');
			napalm_targets(this);
			break;
		case 'choice-4':
			console.log('Dismiss');
			dismiss_alerts(this);
			break;
		default:
			console.log('Invalid choice');
	}
}

// ACTIONS

function get_all_alerts() {

	$.getJSON( "/webcli/connect", function( alerts ) {
		console.log('test');

		for (var i = 0; i < alerts.length; i++) {

			current_alerts.add(alerts[i]);
		}

	});
}

/* dismiss_alerts()
 *
 */
function dismiss_alerts(form) {
	

	console.log($(form));
	var tbody = $(form).find('tbody');
	console.log(tbody);
	var alert_location = tbody.attr('id');
	console.log('send this: '+alert_location);
	
	alerts = [];
	alerts.push({ 'id' : alert_location });
	$.ajax({
    	type: 'POST',
    	url: 'alert/dismiss',
		data: JSON.stringify(alerts),
    	success: function(data) { console.log(data); },
    	contentType: "application/json",
    	dataType: 'json'
	});
}


/* request_disconnect()
 *
 */
function request_disconnect(socket) {

	socket.emit('disconnect request');
}

function napalm_targets(form) {


	console.log($(form));
	var tbody = $(form).find('tbody');
	var alert_location = tbody.attr('id');
	var alerts = [ { 'id' : alert_location } ];
	console.log('alert is: '+alerts);
	$.ajax({
    	type: 'POST',
    	url: '/napalm',
		data: JSON.stringify(alerts),
    	success: function(data) { console.log(data); },
    	contentType: "application/json",
    	dataType: 'json'
	});

}

function deauth_targets(form) {


	console.log($(form));
	var tbody = $(form).find('tbody');
	var alert_location = tbody.attr('id');
	var alerts = [ { 'id' : alert_location } ];
	console.log('alert is: '+alerts);
	$.ajax({
    	type: 'POST',
    	url: '/deauth',
		data: JSON.stringify(alerts),
    	success: function(data) { console.log(data); },
    	contentType: "application/json",
    	dataType: 'json'
	});

}
