module instruction_memory (
    input  [31:0] pc,
    output reg [31:0] instruction
);
    localparam [3:0] OP_ADD    = 4'b0000;
    localparam [3:0] OP_SUB    = 4'b0001;
    localparam [3:0] OP_AND    = 4'b0010;
    localparam [3:0] OP_OR     = 4'b0011;
    localparam [3:0] OP_XOR    = 4'b0100;
    localparam [3:0] OP_LOADI  = 4'b0101;
    localparam [3:0] OP_LOADHI = 4'b0110;
    localparam [3:0] OP_MAC4   = 4'b1000;

    always @(*) begin
        case (pc[5:2])
            4'd0: instruction = {OP_LOADI, 4'd1, 4'd0, 4'd0, 16'h0201};
            4'd1: instruction = {OP_LOADHI,4'd1, 4'd1, 4'd0, 16'h0403};
            4'd2: instruction = {OP_LOADI, 4'd2, 4'd0, 4'd0, 16'h0605};
            4'd3: instruction = {OP_LOADHI,4'd2, 4'd2, 4'd0, 16'h0807};
            4'd4: instruction = {OP_MAC4,  4'd3, 4'd1, 4'd2, 16'h0000};
            4'd5: instruction = {OP_ADD,   4'd4, 4'd3, 4'd0, 16'h0000};
            4'd6: instruction = {OP_XOR,   4'd5, 4'd1, 4'd2, 16'h0000};
            default: instruction = 32'h0000_0000;
        endcase
    end
endmodule
