    function getHeight(elemID) {
        e = document.getElementById(elemID);
        if (e) {
            return e.offsetHeight;
        } else {
            return 0;
        }
    }
    function getFrameHeight() {
        var h = 300;
        if( typeof( window.innerWidth ) == 'number' ) {
          //Non-IE
          h = window.innerHeight;
        } else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) {
          //IE 6+ in 'standards compliant mode'
          h = document.documentElement.clientHeight;
        }
        return h
    }
    function fillFrame(elem) {
        h = getFrameHeight() - OFFSET_PX;
        elem.style.height = h + "px";
        document.body.style.overflow = "hidden"; // prevent iframe scrolling (necessary for FF)        
    }
    function scrollBox(elem) {
        h = getFrameHeight() - getHeight('um_header') - getHeight('footer') - OFFSET_PX;
        elem.style.height = h + "px";
        document.body.style.overflow = "hidden"; // prevent iframe scrolling (necessary for FF)        
    }
