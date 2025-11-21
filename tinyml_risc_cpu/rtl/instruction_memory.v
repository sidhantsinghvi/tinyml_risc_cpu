module instruction_memory (
    input  [31:0] pc,
    output reg [31:0] instruction
);
    localparam [3:0] OP_ADD     = 4'b0000;
    localparam [3:0] OP_SUB     = 4'b0001;
    localparam [3:0] OP_AND     = 4'b0010;
    localparam [3:0] OP_OR      = 4'b0011;
    localparam [3:0] OP_XOR     = 4'b0100;
    localparam [3:0] OP_LOADI   = 4'b0101;
    localparam [3:0] OP_LOADHI  = 4'b0110;
    localparam [3:0] OP_MAC4    = 4'b1000;
    localparam [3:0] OP_CONV3   = 4'b1101;
    localparam [3:0] OP_SIGMOID = 4'b1110;
    localparam [3:0] OP_ACC     = 4'b1111;

    always @(*) begin
        case (pc[6:2])
            5'd0:  instruction = {OP_LOADI,  4'd1, 4'd0, 4'd0, 16'h0201};
            5'd1:  instruction = {OP_LOADHI, 4'd1, 4'd1, 4'd0, 16'h0403};
            5'd2:  instruction = {OP_LOADI,  4'd2, 4'd0, 4'd0, 16'h0605};
            5'd3:  instruction = {OP_LOADHI, 4'd2, 4'd2, 4'd0, 16'h0807};
            5'd4:  instruction = {OP_MAC4,   4'd3, 4'd1, 4'd2, 16'h0000};
            5'd5:  instruction = {OP_ADD,    4'd4, 4'd3, 4'd0, 16'h0000};
            5'd6:  instruction = {OP_XOR,    4'd5, 4'd1, 4'd2, 16'h0000};
            5'd7:  instruction = {OP_LOADI,  4'd4, 4'd0, 4'd0, 16'hFE01};
            5'd8:  instruction = {OP_LOADHI, 4'd4, 4'd4, 4'd0, 16'h0003};
            5'd9:  instruction = {OP_LOADI,  4'd5, 4'd0, 4'd0, 16'h0102};
            5'd10: instruction = {OP_LOADHI, 4'd5, 4'd5, 4'd0, 16'h00FF};
            5'd11: instruction = {OP_CONV3,  4'd6, 4'd4, 4'd5, 16'h0000};
            5'd12: instruction = {OP_LOADI,  4'd7, 4'd0, 4'd0, 16'h0064};
            5'd13: instruction = {OP_SIGMOID,4'd8, 4'd7, 4'd0, 16'h0000};
            5'd14: instruction = {OP_LOADI,  4'd9, 4'd0, 4'd0, 16'hFFB0};
            5'd15: instruction = {OP_LOADHI, 4'd9, 4'd9, 4'd0, 16'hFFFF};
            5'd16: instruction = {OP_SIGMOID,4'd10,4'd9, 4'd0, 16'h0000};
            5'd17: instruction = {OP_ACC,    4'd0, 4'd3, 4'd0, 16'h0000};
            5'd18: instruction = {OP_ACC,    4'd0, 4'd6, 4'd0, 16'h0000};
            5'd19: instruction = {OP_ACC,    4'd0, 4'd10,4'd0, 16'h0000};
            default: instruction = 32'h0000_0000;
        endcase
    end
endmodule
