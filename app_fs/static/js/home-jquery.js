$(function() {
	getTreeMenu();
	userLogin();
	fileOperation();
	help();
});

function getTreeMenu() {
	$.ajax({
		url: '/ajax/treeMenu/',
		type: 'POST',
		data: {
			flag: '1'
		},
		success: function(res) {
			if(res.code == '1') {
				var content = res.data;

				var tree = '<ul id="tree" class="filetree treeview-famfamfam"><li id="root"><span class="getSelected folder">root</span></li></ul>';

				$('#filePath').empty().html('<p>PATH: root</p>');
				$('#treeMenu').empty().html(tree);

				createTree(content);

				$("#tree").treeview({
					animated: 'normal',
					persist: 'cookie',
				});
				
				readFile();

				smartMenu();
			}					
		},
		error: function(XMLHttpRequest) {
			alert(XMLHttpRequest.readyState);
			alert(XMLHttpRequest.status);
		}
	});
}

function createTree(content) {

	for (var i = 0; i < content.length; i++) {
		for (var j = 0; j < content[i].length; j++) {

			var data = createTreeNode(content[i][j]);

			//需将id中的/转义
			var id = data[1].replace(/\//g, '\\/');
			var $root = $('#tree').find('li[id=' + id + ']');

			if($root.children().length == 1) {
				$root.append('<ul></ul>');				
			}
			$root.find('ul').append(data[0]);
		}
	}
}

function createTreeNode(content) {
	var node = '';
	var flag = '';
	var parent = '';
	var path = '';
	var name = '';
	var item = [];

	if (content[0] == '0') {
		flag = 'folder';
	} else {
		flag = 'file';
	}
	path = content.substring(1);
	item = content.split('/');
	name = item[item.length - 1];

	node = '<li id="' + path + '"><span class="' + flag + '">' + name + '</span></li>';

	parent = content.substring(1, content.length - name.length - 1);

	return [node, parent];
}

function userLogin() {
	$('#usernameList').on('click', 'li', function() {
		var $this = $(this);
		var name = $(this).text();
		$('#loginModal').modal();
		$('#username').empty().html('<p>' + name + '</p>');
		
		$('#login').click(function() {
			var pwd = $('#InputPassword').val();
			$.ajax({
				url: '/ajax/login',
				type: 'POST',
				tradition: true,
				data: {
					username: name,
					password: pwd
				},
				success: function(res) {
					if(res['code'] == '1' && name == 'Root') {
						$('.active').removeClass('active');
						$this.addClass('active');
						$('.hidden').removeClass('hidden');
						$('.disabled').removeClass('disabled');
					} else {
						alert(res['msg']);
					}
				},
				error: function(XMLHttpRequest) {
					alert(XMLHttpRequest.readyState);
					alert(XMLHttpRequest.status);
				}
			});
		});		
	});		
}

function fileOperation() {
	$('#fileOperationList').on('click', 'li', function() {
		if($(this).children().text() == 'Save') {
			var path = $('#filePath > p').text().substring(6);
			var contents = $('#fileText').val(); //能体现换行符

			$.ajax({
				url: '/ajax/reviseFile',
				type: 'POST',
				data: {
					path: path,
					contents: contents
				},
				success: function(res) {
					if(res.code == '1') {
						alert('success');
					}
				},
				error: function(res) {

				}
			});
		}
		else if($(this).children().text() == 'New File') {
			$('#newFileModal').modal();
			$('#newFile').click(function() {
				var name = $('#InputFileName').val();
				var path = $('#filePath > p').text().substring(6);				
				path = path + '/' + name;

				// 转义正斜杠
				var id = path.replace(/\//g, '\\/');
				// 转义点
				id = id.replace(/\./g, '\\.');

				var $result = $('#tree').find('li[id=' + id + ']');

				if(!$result.length) {
					var myDate = new Date();
					var year = myDate.getFullYear();
					var month = myDate.getMonth() + 1;
					var day = myDate.getDate();
					var date = year + '/' + month + '/' + day;

					var contents = '';
					$.ajax({
						url: '/ajax/createFile',
						type: 'POST',
						data: {
							path: path,
							name: name,
							date: date,
							kind: '1',
							contents: contents
						},
						success: function(res) {
							if(res.code == '1') {
								getTreeMenu();
							}
						},
						error: function(res) {
						}
					});
				} else {
					alert('File already exsited!')
				}
											
			});
		}
		else if($(this).children().text() == 'New Folder') {
			$('#newFileModal').modal();
			$('#newFile').click(function() {
				var name = $('#InputFileName').val();
				var path = $('#filePath > p').text().substring(6);
				path = path + '/' + name;

				// 转义正斜杠
				var id = path.replace(/\//g, '\\/');

				var $result = $('#tree').find('li[id=' + id + ']');
				if(!$result.length) {
					var myDate = new Date();
					var year = myDate.getFullYear();
					var month = myDate.getMonth() + 1;
					var day = myDate.getDate();
					var date = year + '/' + month + '/' + day;

					var contents = '';
					$.ajax({
						url: '/ajax/createFile',
						type: 'POST',
						data: {
							path: path,
							name: name,
							date: date,
							kind: '0',
							contents: contents
						},
						success: function(res) {
							if(res.code == '1') {
								getTreeMenu();
							}
						},
						error: function(res) {
						}
					});
				} else {
					alert('Folder already exsited!');
				}
								
			});
		}
		else if($(this).children().text() == 'Delete') {
			var path = $('#filePath > p').text().substring(6);
				
			$.ajax({
				url: '/ajax/deleteFile',
				type: 'POST',
				data: {
					path: path
				},
				success: function(res) {
					if(res.code == '1') {
						getTreeMenu();
					}
				},
				error: function(res) {
					}
			});		
		}
		else if($(this).children().text() == 'Property') {
			var path = $('#filePath > p').text().substring(6);
				
			$.ajax({
				url: '/ajax/readFCB',
				type: 'POST',
				data: {
					path: path
				},
				success: function(res) {
					if(res.code == '1') {
						$('#fileInfoModal').modal();
						var content = res.data;
						$('#pathInfo').empty().html('<p>' + content['path'] + '</p>');
						$('#nameInfo').empty().html('<p>' + content['name'] + '</p>');
						$('#sizeInfo').empty().html('<p>' + content['size'] + '</p>');
						$('#dateInfo').empty().html('<p>' + content['date'] + '</p>');
						$('#kindInfo').empty().html('<p>File</p>');
						$('#blockInfo').empty().html('<p>' + content['startIndexBlock'] + '</p>');			
					}
				},
				error: function(XMLHttpRequest) {
					alert(XMLHttpRequest.readyState);
					alert(XMLHttpRequest.status);
				}
			});		
		}
		else {

		}
	});
}

function readFile() {

	$('.folder').click(function() {
		$('.getSelected').removeClass('getSelected');
		$(this).addClass('getSelected');
		var path = $(this).parent().attr('id');
		$('#filePath').empty().html('<p>PATH: ' + path + '</p>');
	});

	$('.file').click(function() {
		$('.getSelected').removeClass('getSelected');
		$(this).addClass('getSelected');

		var path = $(this).parent().attr('id');
		$('#filePath').empty().html('<p>PATH: ' + path + '</p>');
		
		$.ajax({
			url: '/ajax/readFile',
			type: 'POST',
			data: {
				path: path
			},
			success: function(res) {
				if(res.code == '1') {
					var content = res.data;
					$('#fileText').val(content);	//能体现换行符
					// $('#fileText').text(content); 	//不能体现换行符
				}
			},
			error: function(XMLHttpRequest) {
				alert(XMLHttpRequest.readyState);
				alert(XMLHttpRequest.status);
			}
		});
	});
}

function smartMenu() {
	var fileMenuData = [
		[{
			text: 'Rename',
			func: function() {
				$('.getSelected').removeClass('getSelected');
				$(this).addClass('getSelected');

				var path = $(this).parent().attr('id');
				$('#filePath').empty().html('<p>PATH: ' + path + '</p>');

				$('#renameModal').modal();
				$('#rename').click(function() {
					var name = $('#InputNewName').val();
					$.ajax({
						url: '/ajax/rename',
						type: 'POST',
						data: {
							path: path,
							name: name
						},
						success: function(res) {
							if(res.code == '1') {
								getTreeMenu();
							}
						},
						error: function(res) {
						}
					});
					return false;
				});								
			}
		},
		{
			text: 'Open',
			func: function() {
				$('.getSelected').removeClass('getSelected');
				$(this).addClass('getSelected');

				var path = $(this).parent().attr('id');
				$('#filePath').empty().html('<p>PATH: ' + path + '</p>');
				
				$.ajax({
					url: '/ajax/readFile',
					type: 'POST',
					data: {
						path: path
					},
					success: function(res) {
						if(res.code == '1') {
							var content = res.data;
							$('#fileText').val(content);	//能体现换行符
							// $('#fileText').text(content); 	//不能体现换行符
						}
					},
					error: function(XMLHttpRequest) {
						alert(XMLHttpRequest.readyState);
						alert(XMLHttpRequest.status);
					}
				});
				return false;
			}
		},
		{
			text: 'Delete File',
			func: function() {
				$('.getSelected').removeClass('getSelected');
				$(this).addClass('getSelected');

				var path = $(this).parent().attr('id');
				$('#filePath').empty().html('<p>PATH: ' + path + '</p>');

				$.ajax({
					url: '/ajax/deleteFile',
					type: 'POST',
					data: {
						path: path
					},
					success: function(res) {
						if(res.code == '1') {
							getTreeMenu();
						}
					},
					error: function(res) {
					}
				});
				return false;
			}
		},
		{
			text: 'Property',
			func: function() {
				$('.getSelected').removeClass('getSelected');
				$(this).addClass('getSelected');

				var path = $(this).parent().attr('id');
				$('#filePath').empty().html('<p>PATH: ' + path + '</p>');
				
				$.ajax({
					url: '/ajax/readFCB',
					type: 'POST',
					data: {
						path: path
					},
					success: function(res) {
						if(res.code == '1') {
							$('#fileInfoModal').modal();
							var content = res.data;
							$('#pathInfo').empty().html('<p>' + content['path'] + '</p>');
							$('#nameInfo').empty().html('<p>' + content['name'] + '</p>');
							$('#sizeInfo').empty().html('<p>' + content['size'] + '</p>');
							$('#dateInfo').empty().html('<p>' + content['date'] + '</p>');
							$('#kindInfo').empty().html('<p>File</p>');
							$('#blockInfo').empty().html('<p>' + content['startIndexBlock'] + '</p>');			
						}
					},
					error: function(XMLHttpRequest) {
						alert(XMLHttpRequest.readyState);
						alert(XMLHttpRequest.status);
					}
				});
				return false;
			}
		}]
	];

	var folderMenuData = [
		[{
			text: 'New File',
			func: function() {
				$('.getSelected').removeClass('getSelected');
				$(this).addClass('getSelected');

				var path = $(this).parent().attr('id');
				$('#filePath').empty().html('<p>PATH: ' + path + '</p>');

				$('#newFileModal').modal();
				$('#newFile').click(function() {
					var name = $('#InputFileName').val();
					path = path + '/' + name;

					// 转义正斜杠
					var id = path.replace(/\//g, '\\/');
					// 转义点
					id = id.replace(/\./g, '\\.');

					var $result = $('#tree').find('li[id=' + id + ']');

					if(!$result.length) {
						var myDate = new Date();
						var year = myDate.getFullYear();
						var month = myDate.getMonth() + 1;
						var day = myDate.getDate();
						var date = year + '/' + month + '/' + day;

						var contents = '';
						$.ajax({
							url: '/ajax/createFile',
							type: 'POST',
							data: {
								path: path,
								name: name,
								date: date,
								kind: '1',
								contents: contents
							},
							success: function(res) {
								if(res.code == '1') {
									getTreeMenu();
								}
							},
							error: function(res) {
							}
						});
					} else {
						alert('File already exsited!');
					}
					
					
				});
				getTreeMenu();				
			}
		},
		{	
			// 需要迭代，未完成		
			text: 'Rename',
			func: function() {
				$('.getSelected').removeClass('getSelected');
				$(this).addClass('getSelected');

				var path = $(this).parent().attr('id');
				$('#filePath').empty().html('<p>PATH: ' + path + '</p>');

				$('#renameModal').modal();
				$('#rename').click(function() {
					var name = $('#InputNewName').val();
					$.ajax({
						url: '/ajax/rename',
						type: 'POST',
						data: {
							path: path,
							name: name
						},
						success: function(res) {
							if(res.code == '1') {
								getTreeMenu();
							}
						},
						error: function(XMLHttpRequest) {
							alert(XMLHttpRequest.readyState);
							alert(XMLHttpRequest.status);
						}
					});					
				});	
				return false;		
			}
		}],
		[{
			text: 'New Folder',
			func: function() {
				$('.getSelected').removeClass('getSelected');
				$(this).addClass('getSelected');

				var path = $(this).parent().attr('id');
				$('#filePath').empty().html('<p>PATH: ' + path + '</p>');

				$('#newFileModal').modal();
				$('#newFile').click(function() {
					var name = $('#InputFileName').val();
					path = path + '/' + name;

					// 转义正斜杠
					var id = path.replace(/\//g, '\\/');

					var $result = $('#tree').find('li[id=' + id + ']');
					if(!$result.length) {
						var myDate = new Date();
						var year = myDate.getFullYear();
						var month = myDate.getMonth() + 1;
						var day = myDate.getDate();
						var date = year + '/' + month + '/' + day;

						var contents = '';
						$.ajax({
							url: '/ajax/createFile',
							type: 'POST',
							data: {
								path: path,
								name: name,
								date: date,
								kind: '0',
								contents: contents
							},
							success: function(res) {
								if(res.code == '1') {
									getTreeMenu();
								}
							},
							error: function(res) {
							}
						});
					} else {
						alert('Folder already exsited!');
					}
										
				});
				return false;
			}
		},
		{
			text: 'Delete Folder',
			func: function() {
				$('.getSelected').removeClass('getSelected');
				$(this).addClass('getSelected');

				var path = $(this).parent().attr('id');
				$('#filePath').empty().html('<p>PATH: ' + path + '</p>');

				$.ajax({
					url: '/ajax/deleteFile',
					type: 'POST',
					data: {
						path: path
					},
					success: function(res) {
						if(res.code == '1') {
							getTreeMenu();
						}
					},
					error: function(res) {
					}
				});
				return false;
			}
		},
		{
			text: 'Property',
			func: function() {
				$('.getSelected').removeClass('getSelected');
				$(this).addClass('getSelected');

				var path = $(this).parent().attr('id');
				$('#filePath').empty().html('<p>PATH: ' + path + '</p>');
				
				$.ajax({
					url: '/ajax/readFCB',
					type: 'POST',
					data: {
						path: path
					},
					success: function(res) {
						if(res.code == '1') {
							$('#fileInfoModal').modal();
							var content = res.data;
							$('#pathInfo').empty().html('<p>' + content['path'] + '</p>');
							$('#nameInfo').empty().html('<p>' + content['name'] + '</p>');
							$('#sizeInfo').empty().html('<p>' + content['size'] + '</p>');
							$('#dateInfo').empty().html('<p>' + content['date'] + '</p>');
							$('#kindInfo').empty().html('<p>Folder</p>');
							$('#blockInfo').empty().html('<p>' + content['startIndexBlock'] + '</p>');			
						}
					},
					error: function(XMLHttpRequest) {
						alert(XMLHttpRequest.readyState);
						alert(XMLHttpRequest.status);
					}
				});
				return false;
			}
		}]
	];

	$('.file').smartMenu(fileMenuData, {
		name: 'file'
	});
	$('.folder').smartMenu(folderMenuData, {
		name: 'folder'
	});
}

function help() {
	$('#helpList').on('click', 'li', function() {
		$('#aboutSystemModal').modal();
		$.ajax({
			url: 'ajax/about',
			type: 'POST',
			data: {
				flag: '1'
			},
			success: function(res) {
				if(res.code == '1') {
					var content = '<p>' + res.content + '</p>';
					$('#aboutSystem').empty().html(content);
				}				
			}
		});
	});
}