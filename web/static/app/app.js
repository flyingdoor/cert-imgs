// 创建Vue的实例
Vue.config.delimiters = ['${','}']
new Vue({

    // 绑定id为app的元素
    el: "#app",
    delimiters: ['${', '}'],
    // 数据
    data: {
        message: "hello Vue!",
        checkedRows : [],
        listData  : [],
        tableData:[],
        multipleSelection: [],
        visible: false,
        fileList:[],
        export_result: {},
        show_export_result: false,
        form : {

        },
        exportFormShowFlag:false,
        exportFormLoading: false,
        exportFormLabelWidth:'80px',
        exportForm: {
        }
    },

    mounted() {
      this.query()
    },

    methods: {

        query() {
                fetch('/api/query').then(res => res.json()).then(res => {
                    console.log(res)
                    this.listData = res.data
                    this.tableData = res.data
                })
            },
        add() {
                fetch('/api/query').then(res => res.json()).then(res => {
                    console.log(res)
                    this.listData = res.data
                })
            },
        export_doc() {
            this.multipleSelection
            data = {
                'records': this.multipleSelection,
                'watermarkText': this.exportForm.watermarkText,
            }
            console.log(this.checkedRows)
            console.log(data)
            fetch('/api/gen_doc', {
                    'method': 'POST',
                    'body': JSON.stringify(data)
                })
            .then(res => res.json()).then(res => {
                    console.log(res)
                    this.export_result = res
                    this.show_export_result = true
                })
        },
        onSubmit() {
            this.form.fileList = this.fileList
            console.log(this.form)

            fetch('/api/add', {
                    'method': 'POST',
                    'body': JSON.stringify({
                            'name': this.form.name,
                            'category': this.form.category,
                            'images': this.form.fileList
                        })
                })
            .then(res => res.json()).then(res => {
                    console.log(res)
                    this.query()
                    if(res && res.success) {
                        this.form={}
                        this.fileList=[]
                    }

                })
//            console.log(this.fileList)
        },
        handleUploadSuccess(response, file, fileList) {
            console.log(response)
            console.log(fileList)
            this.fileList.push(response)
        },
        handleRemove(file, fileList) {
            console.log(file, fileList);
        },

        handlePreview(file) {
            console.log(file);
        },

        toggleSelection(rows) {
        if (rows) {
          rows.forEach(row => {
            this.$refs.multipleTable.toggleRowSelection(row);
          });
        } else {
          this.$refs.multipleTable.clearSelection();
        }
      },
      handleSelectionChange(val) {
        this.multipleSelection = val;
      },
      handleDelete(index, row) {
        console.log(index);
        console.log(row);

        fetch('/api/delete', {
                    'method': 'POST',
                    'body': JSON.stringify({
                            'uk': row.uk
                        })
                })
            .then(res => res.json()).then(res => {
                    console.log(res)
                    this.query()
                })
      },
      exportFormCancel() {
        this.exportFormShowFlag = false
        }
    },
    rules : {
    }

})
//
//$('#table').bootstrapTable({
//  url: '/api/query',
//  pagination: true,
//  search: true,
//  columns: [{
//    field: 'id',
//    title: 'Item ID'
//  }, {
//    field: 'name',
//    title: 'Item Name'
//  }, {
//    field: 'price',
//    title: 'Item Price'
//  }]
//})

