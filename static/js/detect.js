(function () {
	'use strict';

	const devtools = {
		isOpen: false,
		orientation: undefined
	};

	const threshold = 160;
	const threshold_height = 210;

	const emitEvent = (isOpen, orientation) => {
		window.dispatchEvent(new CustomEvent('devtoolschange', {
			detail: {
				isOpen,
				orientation
			}
		}));
	};

	setInterval(() => {
		const widthThreshold = window.outerWidth - window.innerWidth > threshold;
		const heightThreshold = window.outerHeight - window.innerHeight > threshold_height;
		const orientation = widthThreshold ? 'vertical' : 'horizontal';

		if (
			!(heightThreshold && widthThreshold) &&
			((window.Firebug && window.Firebug.chrome && window.Firebug.chrome.isInitialized) || widthThreshold || heightThreshold)
		) {
			if (!devtools.isOpen || devtools.orientation !== orientation) {
				emitEvent(true, orientation);
			}

			devtools.isOpen = true;
			devtools.orientation = orientation;
		} else {
			if (devtools.isOpen) {
				emitEvent(false, undefined);
			}

			devtools.isOpen = false;
			devtools.orientation = undefined;
		}
	}, 500);

	if (typeof module !== 'undefined' && module.exports) {
		module.exports = devtools;
	} else {
		window.devtools = devtools;
	}

	window.addEventListener('load', function(){
		var url = location.href;
		var host = location.host;
		var protocol= location.protocol;
		if (window.devtools.isOpen) {
		  if ( url.indexOf('error/') != -1) {
			return;
		  }
		  location.href = protocol+'//'+host+'/403';
		}
		window.addEventListener('devtoolschange', event => {
			if (event.detail.isOpen) {
				if ( url.indexOf('error/') != -1) {
					return;
				}
				location.href = protocol+'//'+host+'/403';
			}
		  });
	  });
})();