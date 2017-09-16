var LogApp = LogApp || {};

LogApp.log = function (data, level) {
    var server = '10.11.100.225',
        port = 8001;

    $.post(
      'http://'+server+':'+port+'/api/logger',
      {
        context   :   navigator.userAgent,
        level     :   level || 'error',
        dataType  :   'jsonp',
        data      :   data
      }
    );
  };


LogApp.testLog = function testLog() {
      try {
        // some function

        throw new Error('my thrown message')

      } catch (e) {
        log({
          error : e.message
        });
      }

    log('in func testLog where e.message seem not to work', 'info');

    };

