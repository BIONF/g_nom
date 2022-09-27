import { Component } from 'react';
import Plot from 'react-plotly.js';
import { fetchTaxaminerScatterplot } from '../../../../../../../../api';
const colors = require("./colors.json");

interface Props {
	sendClick: Function
	e_value: number
	show_unassigned: boolean
    scatter_data: any
	userID: number
	token: string
}

/**
 * Main Scatterplot Component
 */
class ScatterMatrix extends Component<Props, any> {
	constructor(props: any){
		super(props);
		this.state ={ 
			data: [] , // raw JSON data
			traces: [], // traces dicts for plotly
			selected_gene: "", // g_name
			aa_seq: "", // inherited
			ui_revision: "true", // bound to plot to preserve camera position
			auto_size: true, // automatically size dots in scatterplot
			marker_size: 5, // actual dot size in the plot
			manual_size: 5, // dot size selected by user
			color_options: colors.options, // color palette options
			camera_ratios: {xy: 1.0, xz: 1.0, yz: 1.0}
		}
        this.sendClick = this.sendClick.bind(this);
	}

	/**
	 * Call API on component mount to load plot data
	 */
	componentDidMount() {
		fetchTaxaminerScatterplot(1, 1, this.props.userID, this.props.token)
		.then(data => {
			this.setState( {data: data} );
			this.set_auto_size(data);
			this.build_plot();
		})
	}

	/**
	 * A dot in the plot was clicked => pass to parent
	 * @param e Plot OnClick() event
	 */
    sendClick(e: any){
		this.props.sendClick(e.g_name);
    }

	/**
	 * This fixes a problem where some interactions reset the camera.
	 * Manually updating the uirevision state blocks plot resets
	 * @returns True (as required by OnLegendClick() => )
	 */
	lock_uirevision(){
		this.setState({ ui_revision: "true" })
		return(true)
	}

	/**
	 * Set automatic marker size
	 */
	set_auto_size(data: any){
		if (data == undefined) {
			data = this.state.data
		}
		let total_points = 0;
		// overall size of all trace arrays
		for (var trace of data) {
			total_points = total_points + trace.length
		}
		// this was chosen arbitrarily
		let new_size = 65 - Math.round(total_points / 10)
		// set a minimum size arbitrarily
		if (new_size < 3) {
			new_size = 3
		}
		this.setState( { marker_size: new_size } )
	}


	/**
	 * 
	 * @returns Set scatterplot axis
	 */
    set_axis() {
        return(
            {
                showline:false,
                zeroline:false,
                gridcolor:'#ffff',
                ticklen:2,
                tickfont:{size:10},
                titlefont:{size:12}
              }
        )
    }


	/**
	 * Convert API data into plotly traces
	 * @param data API data
	 * @returns list of traces
	 */
	transformData (data: any[], legendonly: any[]) {
		let legendonly_names: string[] = []

		legendonly.forEach((dot: any) => {
			legendonly_names.push(dot.name)
		})

		// Avoid NoneType Exceptions
		if (data == null) {
			return []
		}

        const traces: any[] = []
        data.map(each => {
		    const x : string[] = [];
		    const y : string[] = [];
            const z : string[] = [];
            let label = "";
			let gene_name = "";
            const my_customdata : any = [];
            let chunk = each;

			// push 3D coordinates in arrays accordingly
		    chunk.map((each: { [x: string]: string; }) => {
                // filter by e-value
				if(parseFloat(each['bh_evalue']) < this.props.e_value) {
					x.push(each['Dim.1'])
					y.push(each['Dim.2'])
					z.push(each['Dim.3'])
					label = each['plot_label']
					gene_name = each['g_name']
					my_customdata.push([each['plot_label'], each['g_name'], each['best_hit'], each['bh_evalue'], each['taxon_assignment'], each['c_name']])
				} 
				// Include unassigned data points (which usually don't have a e-value)
				else if(this.props.show_unassigned === true && each['plot_label'] === 'Unassigned') {
					x.push(each['Dim.1'])
					y.push(each['Dim.2'])
					z.push(each['Dim.3'])
					label = each['plot_label']
					my_customdata.push([each['plot_label'], each['g_name'], each['best_hit'], each['bh_evalue'], each['taxon_assignment'], each['c_name']])
				} else {
					//console.log(each['g_name'])
				}
		    })

			// Setup the plot trace
			let visible = undefined
			if (legendonly_names.includes(label)) {
				visible = "legendonly"
			} else {
				visible = true
			}

			// plotly trace
            const trace = {
                type: 'splom',
                dimensions: [
                    {label: "Dim.1", values: x},
                    {label: "Dim.2", values: y},
                    {label: "Dim.3", values: z},
                ],
                name: label,
                text: label,
				visible: visible,

				// track the unique gene name
				customdata: my_customdata,
				hovertemplate: "%{customdata[0]} <br>%{customdata[1]} <br><extra>Best hit: %{customdata[2]} <br>Best hit e-value: %{customdata[3]} <br> </extra>"

            }
            traces.push(trace)
        })
		return traces
	}

	/**
	 * Handle Selection events
	 * @param points plotly points
	 */
	handleSelection(points: any) {
		let selected_ids: string[] = []

		points.map((each: any) => {
			selected_ids.push(each.customdata[1])
		})

		// pass data up
		this.props.sendClick(selected_ids)
	}

	/**
	 * Build the 3D scatterplot
	 * @returns Plotly Plot as React component
	 */
	build_plot() {
		return (
			<Plot
				divId='scattermatrix'
					data = {this.transformData(this.state.data, this.props.scatter_data.legendonly)}
					layout = {{
						autosize: true,
						showlegend: true,
						uirevision: this.state.ui_revision,
						// @ts-ignore
						// overrides are incomplete here, ignore for now
						legend: {itemsizing: 'constant', orientation: "h", y: -0.25,
                        xaxis:this.set_axis(),
                        yaxis:this.set_axis(),
                        xaxis2:this.set_axis(),
                        xaxis3:this.set_axis(),
                        yaxis2:this.set_axis(),
                        yaxis3:this.set_axis(),
                        yaxis4:this.set_axis()},
						colorway : colors.palettes[this.props.scatter_data.colors]
						}}
                    style = {{width: "100%", height: 700}}

					// disable legend trace selection (=> slave to main plot)
					onLegendClick={() => false}
					onLegendDoubleClick={() => false}
					onSelected={(e:any) => this.handleSelection(e.points)}
				/>
		)
	}

	/**
	 * Render react component
	 * @returns render react component
	 */
	render() {
		return (
			<div>
				{this.build_plot()}
			</div>
		)
	}
}

export default ScatterMatrix;