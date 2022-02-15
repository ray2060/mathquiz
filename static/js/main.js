$('#a_plus_b').submit(function() {
  let a = $('#a').val();
  if (!(a+"").match(/^\d+$/)) {
    $('#error').html('请输入整数A。').show();
    return false;
  }
  let b = $('#b').val();
  if (!(b+"").match(/^\d+$/)) {
    $('#error').html('请输入整数B。').show();
    return false;
  }
});
