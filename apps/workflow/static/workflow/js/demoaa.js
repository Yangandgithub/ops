jsPlumb.ready(function () {
    //储存数据
    var flowGraphList={};
    flowGraphList.widgetList=[];
    flowGraphList.edgeList=[];
	flowGraphList.workflowId = null;
    var selectList=[];
    //注册jsPlumb
    var instance = window.jsp = jsPlumb.getInstance({
        DragOptions: { cursor: "move", zIndex: 2000 },
        ConnectionOverlays: [
            [ "Arrow", {
                location: 1,
                visible:true,
                width:11,
                length:11,
                id:"ARROW",
                events:{
                    click:function() { alert("you clicked on the arrow overlay")}
                }
            } ],
            [ "Label", {
                location: 0.5,
                id: "label",
                cssClass: "aLabel"
            }]
        ],
        Container: "canvas"
    });
    var flag=true;//新增开始节点打开
    var $index=0;
    var flow={
        operation:'',
        editId:'',
        showFlow:false,
        randomString:function(len) {
            len = len || 32;
            var $chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678';
            var maxPos = $chars.length;
            var pwd = '';
            for (var i = 0; i < len; i++) {
                pwd += $chars.charAt(Math.floor(Math.random() * maxPos));
            }
            return pwd;
        },
        randomNumBoth:function (Min,Max){
            var Range = Max - Min;
            var Rand = Math.random();
            var num = Min + Math.round(Rand * Range);
            return num;
        },
        selectListClick:function (e) {
             var dom=$(e).parent().find('li');
             dom.removeClass('active');
             var text=$(e).text();
             var input=$(e).parent().prev().find('input');
             input.val(text);
             $(e).addClass('active');
          //  $("#selectList").hide();
        },
        selectData:function (data,dom) {
            var that=this;
            $("#"+dom).empty();
			var listStr='<li class="active list" style="border-radius: 50%" onmouseover="isTriggered(this)"}>start</li>';
            for(var index=0;index<data.length;index++) {
                listStr += '<li class="list" style="top:'+50*(index+1)+'px">' + data[index].name + '</li>';
            }
            $("#"+dom).append(listStr);
		    $(".leftContainer li").draggable({
        		helper: "clone",
        		scope: "plant",
    		});
			$("#canvas").droppable({
				scope: "plant",
				drop: function(event, ui){
					addFlowNode(ui);
				}
	});

        },
        //全局添加名称减少数据的请求
		//TODO: modify the url location
        selectListFn:function () {
           $.ajax({
                 type: "post",
                 url:"/workflow/workflow_task/",
				 data: {"mode": "getNodes"},
                 dataType: "json",
                 success: function(data){
					 console.log(data);
                     var obj=data;
                     selectList=obj["nodes"];
                     flow.selectData(selectList,'leftContainer');
                 }
             });
        }
    };
    //全局添加名称减少数据的请求
    flow.selectListFn();
    //$(".leftContainer li").draggable({
        //helper: "clone",
        //scope: "plant",

    //});
    //$(".leftContainer li").mouseover(function () {
        //$(".leftContainer li").removeClass('active').eq($(this).index()).addClass('active')
    //});
    //$("#canvas").droppable({
        //scope: "plant",
        //drop: function(event, ui){
			//alert('XXXXXXX');
            //addFlowNode(ui);
        //}
    //});

   var connectorPaintStyle = {
      strokeWidth:1,
      stroke: "green",
      joinstyle: "round"
    },
    sourceEndpoint = {
      endpoint: "Dot",
      paintStyle: {
            stroke: "transparent",
            fill: "#337AB7",
            radius:5,
            strokeWidth: 10
      },
      maxConnections:50,
      isSource:true,
      connector:["Straight"],
      connectorStyle: connectorPaintStyle,
      overlays: [
        [ "Label", {
          location: [0.5, 0.5],
          //label: "Drag",
          visible:false
        } ]
      ]
    },
    // the definition of target endpoints (will appear when the user drags a connection)
    targetEndpoint = {
      endpoint: "Dot",
      paintStyle: { stroke: "#337AB7" , fill:"transparent", radius:5},
      maxConnections:50,
      dropOptions: { hoverClass: "hover", activeClass: "active" },
      isTarget:true,
      overlays: [
        [ "Label", { location: [0.5, -0.5], label: "Drop", cssClass: "endpointTargetLabel", visible:false } ]
      ]
    },
    init = function (connection,status) {
      connection.getOverlay("label").setLabel(status);
    };
   var _addEndpoints = function (toId, sourceAnchors, targetAnchors) {
    for (var i = 0; i < sourceAnchors.length; i++) {
      var sourceUUID = toId + sourceAnchors[i];
      instance.addEndpoint(toId, sourceEndpoint, {
        anchor: sourceAnchors[i], uuid: sourceUUID
      });
    }
    for (var j = 0; j < targetAnchors.length; j++) {
      var targetUUID = toId + targetAnchors[j];
      instance.addEndpoint(toId, targetEndpoint, { anchor: targetAnchors[j], uuid: targetUUID });
    }
  };
   var _docNum=function(dom,source,target) {
    var targetAnchors=[];
    var  sourceAnchors=[];
    for(var i=0;i<source;i++){
      if(source==1){
        sourceAnchors.push([0.5, 1, 0, 1 ])
      }else{
        sourceAnchors.push([i/(source-1), 1, 0, 1 ])
      }
    }
    for(var i=0;i<target;i++){
      if(target==1){
        targetAnchors.push([0.5,  0, 1, 0])
      }else{
        targetAnchors.push([i/(target-1), 0, 1, 0])
      }

    }
    _addEndpoints(dom,sourceAnchors,targetAnchors);
  };
  $("#canvas").draggable();

  //添加flow
    var addFlowNode=function(ui,parameter){
        var name=$(ui.draggable).text();
        var flowNodeId=flow.randomString(15);
        var list=flowGraphList.widgetList;
        var path='';
        var taskId='';
       //var chooes=true;
        flag=true;
        flow.showFlow=false;
        var nameList=[];
        for(var j=0;j<selectList.length;j++){
            nameList.push(selectList[j].name)
        }
			var str='<div class="window jtk-node" id="' +flowNodeId+ '" ><a class="name" title="'+name+'">'+name+'</a><div class="editFlowNode" style="display: none"  ><span class="deleteFlowNodeClick"></span><span class="editFlowNodeClick"></span></div></div>';

            $("#canvas").append(str);
            //确定位置
            var d=document.getElementById(flowNodeId);
            d.style.left =parseInt(ui.offset.left - $(d).offset().left)+'px';
            d.style.top =parseInt(ui.offset.top - $(d).offset().top)+'px';
            //实现拖拽;
            instance.draggable(d,{containment:true});
            //出口和入口
            if(name=='start'){
                var targetLength=0;
                d.style.borderRadius='50%';
            }else{
                var targetLength=1;
                d.style.borderRadius='5px';
            }
            var sourceLength=1;
            _docNum(flowNodeId,sourceLength,targetLength);

            for(var index=0;index<selectList.length;index++){
                if(selectList[index].name==name){
                    path=selectList[index].path;
                    taskId=selectList[index].taskId;
                }
            }
            var isStart=false;
            if(name=='start'){
                isStart=true
            }
            //添加节点所需数据
            var widget={
                id:flowNodeId,
                name:name,
                isStart:isStart,
                x:d.style.left,
                y:d.style.top,
                path:path,
                taskId:taskId,
                parameter:parameter,
                sourceLength:sourceLength,
                targetLength:targetLength
            };
            flowGraphList.widgetList.push(widget);
        $index++;
    };
    var editFlowNode=function (name,parameter) {


        var editId=flow.editId;
        var list=flowGraphList.widgetList;
        var path='';
        var taskId='';
        flow.showFlow=false;
            for(var index=0;index<selectList.length;index++){
                if(selectList[index].name==name){
                    path=selectList[index].path;
                    taskId=selectList[index].taskId;
                }
            }
            for(var index=0;index<list.length;index++){
                if(list[index].id==editId){
                    list[index].name=name;
                    list[index].parameter=parameter;
                    list[index].path=path;
                    list[index].taskId=taskId;
                    break
                }
            }
            $('#canvas').find("#"+flow.editId).find('.name').text(name);


    };
    var makeFlowJob=function (data) {
        var _that=this;
        flow.showFlow=true;

        flowGraphList.widgetList=[];
        flowGraphList.edgeList=[];
        $('#canvas').empty();
        instance.deleteEveryEndpoint();

        flowGraphList.widgetList=data.widgetList;
        flowGraphList.edgeList=data.edgeList;

        //回显点
        for(var i=0;i<flowGraphList.widgetList.length;i++) {
			var str='<div class="window jtk-node" id="' +flowGraphList.widgetList[i].id+ '" ><a class="name" title="'+flowGraphList.widgetList[i].name+'">'+flowGraphList.widgetList[i].name+'</a><div class="editFlowNode" style="display: none"  ><span class="deleteFlowNodeClick"></span><span class="editFlowNodeClick"></span></div></div>';

            $("#canvas").append(str);
            var d = document.getElementById(flowGraphList.widgetList[i].id);
            d.style.left =flowGraphList.widgetList[i].x;
            d.style.top =flowGraphList.widgetList[i].y;
            instance.draggable(d,{containment:true});
            var sourceLength=flowGraphList.widgetList[i].sourceLength;
            var targetLength=flowGraphList.widgetList[i].targetLength;
            if(flowGraphList.widgetList[i].name=='start'){
                var targetLength=0;
                d.style.borderRadius='50%';
            }else{
                var targetLength=1;
                d.style.borderRadius='5px';
            }
            _docNum(flowGraphList.widgetList[i].id,sourceLength,targetLength);
            $index++;
        }
        //回显连接线
        var edgeListLength=flowGraphList.edgeList.length;
        for(var j=0;j<edgeListLength;j++) {
            var source = flowGraphList.edgeList[j].source;
            var target = flowGraphList.edgeList[j].destination;
            var status=flowGraphList.edgeList[j].status;
            var color='green';
            if(status=='success'){
                color='green';
            }else if(status=='always'){
                color="#337AB7"
            }else if(status=='error'){
                color='red'
            }
            var conn={
                source:source,
                target:target,
                endpoints:["Dot", "Blank"],
                endpointStyle:{fill:"transparent",radius:3},
                anchors:['Bottom','Top'],
                connector:["Straight"],
                paintStyle: { stroke:color, strokeWidth: 1,cornerRadius: 5},
            };
            instance.connect(conn);
        }

    };

    instance.registerConnectionTypes({
        "success":{
            paintStyle:{stroke:"green"},
        },
        "error":{
            paintStyle:{stroke:"red"},
        },
        "always":{
            paintStyle:{stroke:"#337AB7"}
        }
    });
  // suspend drawing and initialise.
  instance.batch(function () {
	// click the edit workflow buttton
	 instance.on(document, "click", ".workflow-btn", function (e) {
		var workflowId = $(this).attr("name");
		flowGraphList.widgetList = [];
        flowGraphList.edgeList = [];
        flowGraphList.workflowId = workflowId;
        $('#canvas').empty();
        instance.deleteEveryEndpoint();

		$("#editWorkflow").show();
    	$.ajax({
    		type: "post",
    		url: "/workflow/workflow_task/",
    		dataType: "json",
    		data: {"workflow_id": workflowId, "mode": "editWorkflow"},
    			"success": function(resp) {

					if (resp["code"] == 0) {
    					var workflowDescription = resp["data"];
						if (workflowDescription != null){
                            makeFlowJob(workflowDescription);
						}

					}
					else {
						console.log('Faild to edit workflow:');
    					window.wxc.xcConfirm("Failed to edit workflow", window.wxc.xcConfirm.typeEnum.error);
					}
				},
				"error": function(response) {
    				window.wxc.xcConfirm("操作失败!", window.wxc.xcConfirm.typeEnum.error);
				}
    	});
    });

    //确定添加node
    instance.on(document, "click", "#clickAddFlow", function (e) {
       var name=$("#"+flow.editId).find('a').attr("title");
       var parameter=$('#parameter').val();
       editFlowNode(name,parameter);
      $("#addFlowMask").hide();
    });
    //取消node添加
    instance.on(document, "click", "#falseAddFlow", function (e) {
        $("#addFlowMask").hide();
    });
    //点击流程node
    instance.on(document, "click", ".jtk-node", function (e) {
       $('.jtk-node').removeClass("jtk-click");
       $('.jtk-node').find(".editFlowNode").hide();
       $(this).addClass("jtk-click");
       $(this).find(".editFlowNode").show();
    });
    //删除流程node
    instance.on(document, "click", ".deleteFlowNodeClick", function (e) {
        if($index>0){
            var deleteNode=this.parentNode.parentNode.id;
            $('#'+deleteNode).remove();
            //删除点
            var list=flowGraphList.widgetList;
            for(var index=0;index<list.length;index++){
                if(list[index].id==deleteNode){
                    list.splice(index,1);
                    break
                }
            }

            //删除点相关的线
            var result=[];
            for(var s=0;s<flowGraphList.edgeList.length;s++){
                if(flowGraphList.edgeList[s].source==deleteNode||flowGraphList.edgeList[s].destination==deleteNode){
                    flowGraphList.edgeList.splice(s,1,0)
                }
            }
            for(var j=0;j<flowGraphList.edgeList.length;j++){
                if(flowGraphList.edgeList[j]!=0){
                    result.push(flowGraphList.edgeList[j])
                }
            }
            flowGraphList.edgeList=result;
            instance.removeAllEndpoints(deleteNode);
        }
        $index--;

      });

    //编辑
      instance.on(document, "click", ".editFlowNodeClick", function (e) {
          var editNode=this.parentNode.parentNode.id;
          $("#addFlowMask").show();
          var parameter='';
          var list=flowGraphList.widgetList;
          for(var index=0;index<list.length;index++){
              if(editNode==list[index].id){
                  parameter=list[index].parameter;
                  break
              }
          }
          $("#parameter").val(parameter);
          flow.editId=editNode;
      });

      //点击连接线事件
      instance.bind("click", function (conn, originalEvent) {
          var edgeList=flowGraphList.edgeList;
          for(var i=0;i<edgeList.length;i++){
              if(edgeList[i].source==conn.sourceId&&edgeList[i].destination==conn.targetId){
                 if(edgeList[i].status=='success'){
                     edgeList[i].status='always';
                     init(conn,'always');
                     conn.setType("always");
                 }else if(edgeList[i].status=='always'){
                     edgeList[i].status='error';
                     init(conn,'error');
                     conn.setType("error");
                 }else if(edgeList[i].status=='error'){
                     edgeList[i].status='success';
                     init(conn,'success');
                     conn.setType("success");
                 }
              }
          }

      });
      //连接事件
      instance.bind("connection", function (connInfo, originalEvent) {

          if(connInfo.sourceId!=connInfo.targetId){
              if(!flow.showFlow){
                  var edge={
                      source:connInfo.sourceId,
                      destination:connInfo.targetId,
                      status:'success'
                  };
                  flowGraphList.edgeList.push(edge);
                  init(connInfo.connection,'success');

              }else{
                  for(var index=0;index<flowGraphList.edgeList.length;index++){
                       if(flowGraphList.edgeList[index].source==connInfo.sourceId&&flowGraphList.edgeList[index].destination==connInfo.targetId){
                       init(connInfo.connection,flowGraphList.edgeList[index].status);
                       }
                   }
              }

          }


      });
      //存储流程数据
      instance.on(document, "click", "#okFlow", function (e) {
          var widgetList=flowGraphList.widgetList;
          var edgeList=flowGraphList.edgeList;
          //记入flownode位置
          for(var index=0;index<widgetList.length;index++){
              widgetList[index].x=$("#canvas").find('#'+widgetList[index].id).css('left');
              widgetList[index].y=$("#canvas").find('#'+widgetList[index].id).css('top');

          }
          var result=[];
          for(var s=0;s<edgeList.length;s++){
              result.push(edgeList[s].source);
              result.push(edgeList[s].destination);
          }
          function unique(arr){
              var newArr = [arr[0]];
              for(var i=1;i<arr.length;i++){
                  if(newArr.indexOf(arr[i]) == -1){
                      newArr.push(arr[i]);
                  }
              }
              return newArr;
          }
          var results=unique(result);
          var widgetLists=[];
          for(var s=0;s<results.length;s++){
              for(var k=0;k<widgetList.length;k++){
                  if(results[s]==widgetList[k].id){
                      widgetLists.push(widgetList[k])
                  }
              }
          }
          flowGraphList.widgetList=widgetLists;
          //工作流提交请求功能
		  //TODO Post workflow definition
          $.ajax({
              type: "post",
              url: "/workflow/workflow_task/",
              data: {"mode": "alterWorkflowDefinition",
				     "workflow_id": flowGraphList.workflowId,
				     "workflow": JSON.stringify(flowGraphList)},
              dataType: "json",
              success: function(data){
                  alert("提交成功")
              }
          });

      });

	instance.on(document, "click", ".close", function (e) {
          $("#editWorkflow").hide();
      });

    instance.bind("connectionDragStop", function (connection) {
        if(connection.sourceId==connection.targetId){
            alert("不能连接自己");
            instance.deleteConnection(connection)
        }
    });
    instance.bind("beforeDetach", function (conn) {
        flow.showFlow=false;
        var edgeList=flowGraphList.edgeList;
          for(var i=0;i<edgeList.length;i++){
              if(edgeList[i].source==conn.sourceId&&edgeList[i].destination==conn.targetId){
                  flowGraphList.edgeList.splice(i,1)
              }
          }
    });
    instance.on(document, "click", "#executeFlow", function (e) {
        //工作流执行功能
        $.ajax({
        	type: "post",
            url: "/workflow/workflow_task_launch/",
            data: {"workflow_id": flowGraphList.workflowId},
            dataType: "json",
            success: function(data){
                alert("提交成功")
            }
          });
      });
      //视图缩放功能
  });
  jsPlumb.fire("jsPlumbDemoLoaded", instance);
});

function isTriggered(op){
    $(".leftContainer li").removeClass('active');
	$(op).addClass('active')
}
